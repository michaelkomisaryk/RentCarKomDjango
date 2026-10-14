import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from accounts.models import Role, User
from fleet.models import Car, CarPhoto

MEDIA_ROOT = tempfile.mkdtemp()


def tiny_png(name="car.png"):
    buffer = BytesIO()
    Image.new("RGB", (8, 8), "red").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def make_user(email, role):
    return User.objects.create_user(email=email, password="secret1", name=email, role=role)


CAR_DATA = {
    "brand": "Skoda",
    "model": "Octavia",
    "year": 2020,
    "price": "40",
    "seats": 5,
    "plate": "SK 0001 KK",
    "color": "White",
    "transmission": "Manual",
    "fuel": "Gasoline",
    "mileage": 1000,
    "description": "A test car",
}


class CatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_cars")

    def test_catalog_lists_the_demo_fleet(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["cars"]), 8)
        self.assertContains(response, "Toyota")
        self.assertContains(response, "Sportage")

    def test_fuel_filter_keeps_matching_cars(self):
        response = self.client.get("/", {"fuel": "Hybrid"})

        brands = [car.brand for car in response.context["cars"]]
        self.assertEqual(brands, ["Hyundai", "Kia"])

    def test_empty_filter_says_nothing_matched(self):
        response = self.client.get("/", {"fuel": "Electric"})

        self.assertContains(response, "No cars match your filters")
        self.assertEqual(len(response.context["cars"]), 0)

    def test_car_page_shows_specs(self):
        car = Car.objects.get(plate="AA 1234 KK")
        response = self.client.get(f"/cars/{car.pk}/")

        self.assertContains(response, "Toyota Camry")
        self.assertContains(response, "AA 1234 KK")
        self.assertContains(response, "Available for Rent")
        self.assertContains(response, "32,000 km")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AdminCarTests(TestCase):
    def test_guest_is_sent_to_login(self):
        response = self.client.get(reverse("car_create"))
        self.assertRedirects(
            response,
            f"/accounts/login/?next={reverse('car_create')}",
            fetch_redirect_response=False,
        )

    def test_client_cannot_add_or_delete_cars(self):
        client = make_user("client@example.com", Role.CLIENT)
        self.client.force_login(client)
        car = Car.objects.create(**{**CAR_DATA, "price": "40"})

        self.assertEqual(self.client.get(reverse("car_create")).status_code, 403)
        self.assertEqual(self.client.post(reverse("car_delete", args=[car.pk])).status_code, 403)
        self.assertTrue(Car.objects.filter(pk=car.pk).exists())

    def test_admin_can_add_a_car_with_a_photo(self):
        admin = make_user("admin-cars@example.com", Role.ADMIN)
        self.client.force_login(admin)

        response = self.client.post(
            reverse("car_create"),
            {**CAR_DATA, "photos": [tiny_png("a.png"), tiny_png("b.png")]},
            follow=True,
        )

        car = Car.objects.get(plate="SK 0001 KK")
        self.assertEqual(car.added_by, admin)
        self.assertEqual(car.photos.count(), 2)
        self.assertContains(response, "Skoda Octavia")
        self.assertContains(response, "added!")

    def test_invalid_year_and_price_are_rejected(self):
        admin = make_user("admin-invalid@example.com", Role.ADMIN)
        self.client.force_login(admin)

        response = self.client.post(
            reverse("car_create"),
            {**CAR_DATA, "year": 1800, "price": "0"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Valid year is required")
        self.assertContains(response, "Valid price is required")
        self.assertFalse(Car.objects.filter(plate="SK 0001 KK").exists())

    def test_admin_can_add_photos_and_delete_the_car(self):
        admin = make_user("admin-delete@example.com", Role.ADMIN)
        self.client.force_login(admin)
        car = Car.objects.create(
            brand="Fiat",
            model="500",
            year=2019,
            price="30",
            plate="FT 500 KK",
            fuel="Gasoline",
            transmission="Manual",
        )

        upload = self.client.post(
            reverse("car_add_photos", args=[car.pk]),
            {"photos": tiny_png()},
            follow=True,
        )
        self.assertContains(upload, "Added 1 photo")
        self.assertEqual(CarPhoto.objects.filter(car=car).count(), 1)

        self.client.post(reverse("car_delete", args=[car.pk]))
        self.assertFalse(Car.objects.filter(pk=car.pk).exists())
        self.assertFalse(CarPhoto.objects.filter(car_id=car.pk).exists())

    def test_add_car_link_is_only_shown_to_admins(self):
        admin = make_user("admin-link@example.com", Role.ADMIN)
        client = make_user("client-link@example.com", Role.CLIENT)

        self.client.force_login(admin)
        self.assertContains(self.client.get(reverse("catalog")), "Add Car")

        self.client.force_login(client)
        self.assertNotContains(self.client.get(reverse("catalog")), "Add Car")
