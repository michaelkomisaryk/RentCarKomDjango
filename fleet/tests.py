import os
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from decimal import Decimal

from django.utils import translation

from accounts.models import Role, User
from fleet.currency import format_money
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
    "car_class": "Comfort",
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
        self.assertEqual(len(response.context["cars"]), 40)
        self.assertContains(response, "Toyota")
        self.assertContains(response, "Sportage")

    def test_fuel_filter_keeps_matching_cars(self):
        response = self.client.get("/", {"fuel": "Hybrid"})

        brands = [car.brand for car in response.context["cars"]]
        self.assertEqual(brands, ["Toyota", "Lexus", "Toyota", "Hyundai", "Volvo"])

    def test_class_filter_keeps_matching_cars(self):
        response = self.client.get("/", {"class": "Premium"})

        cars = list(response.context["cars"])
        self.assertTrue(cars)
        self.assertTrue(all(car.car_class == "Premium" for car in cars))
        self.assertIn("BMW", [car.brand for car in cars])

    def test_transmission_and_seats_filters(self):
        manual = self.client.get("/", {"transmission": "Manual"})
        self.assertEqual(
            [car.model for car in manual.context["cars"]],
            ["Polo", "Clio", "Fabia"],
        )
        seven = self.client.get("/", {"seats": "7"})
        self.assertEqual(
            [car.model for car in seven.context["cars"]],
            ["Touran", "S-Max", "V-Class", "Multivan"],
        )

    def test_search_matches_brand_model_and_plate(self):
        by_model = self.client.get("/", {"q": "yaris"})
        self.assertEqual([car.brand for car in by_model.context["cars"]], ["Toyota"])

        by_plate = self.client.get("/", {"q": "gg 3344"})
        self.assertEqual([car.model for car in by_plate.context["cars"]], ["A4"])

        combined = self.client.get("/", {"q": "Hyundai Tucson", "class": "Comfort"})
        self.assertEqual([car.plate for car in combined.context["cars"]], ["FF 1122 KK"])

    def test_empty_filter_says_nothing_matched(self):
        response = self.client.get("/", {"q": "zzzz-no-such-car"})

        self.assertContains(response, "No cars match your filters")
        self.assertEqual(len(response.context["cars"]), 0)

    def test_ukrainian_switches_the_language_and_shows_hryvnia(self):
        switched = self.client.post(reverse("set_language"), {"language": "uk", "next": "/"}, follow=True)

        self.assertContains(switched, "Доступні авто")
        self.assertContains(switched, "Економ")
        self.assertContains(switched, "1 162 грн")
        self.assertNotContains(switched, "$28")

        self.client.post(reverse("set_language"), {"language": "en", "next": "/"})
        english = self.client.get("/")
        self.assertContains(english, "Available Cars")
        self.assertContains(english, "$28/day")

    def test_money_follows_the_active_language(self):
        with translation.override("en"):
            self.assertEqual(format_money(Decimal("45")), "$45")
            self.assertEqual(format_money(Decimal("45.50")), "$45.5")
        with translation.override("uk"):
            self.assertEqual(format_money(Decimal("45")), "1 867,50 грн")
            self.assertEqual(format_money(Decimal("50")), "2 075 грн")

    def test_car_page_shows_specs(self):
        car = Car.objects.get(plate="KA 2401 IK")
        response = self.client.get(f"/cars/{car.pk}/")

        self.assertContains(response, "Toyota Yaris")
        self.assertContains(response, "KA 2401 IK")
        self.assertContains(response, "Available for Rent")
        self.assertContains(response, "18,400 km")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AdminCarTests(TestCase):
    def test_guest_is_sent_to_login(self):
        response = self.client.get(reverse("fleet:car_create"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('fleet:car_create')}",
            fetch_redirect_response=False,
        )

    def test_client_cannot_add_or_delete_cars(self):
        client = make_user("client@example.com", Role.CLIENT)
        self.client.force_login(client)
        car = Car.objects.create(**{**CAR_DATA, "price": "40"})

        self.assertEqual(self.client.get(reverse("fleet:car_create")).status_code, 403)
        self.assertEqual(self.client.post(reverse("fleet:car_delete", args=[car.pk])).status_code, 403)
        self.assertTrue(Car.objects.filter(pk=car.pk).exists())

    def test_admin_can_add_a_car_with_a_photo(self):
        admin = make_user("admin-cars@example.com", Role.ADMIN)
        self.client.force_login(admin)

        response = self.client.post(
            reverse("fleet:car_create"),
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
            reverse("fleet:car_create"),
            {**CAR_DATA, "year": 1800, "price": "0"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вкажіть коректний рік.")
        self.assertContains(response, "Вкажіть коректну ціну.")
        self.assertFalse(Car.objects.filter(plate="SK 0001 KK").exists())

    def test_ukrainian_price_is_stored_in_dollars(self):
        admin = make_user("admin-uah@example.com", Role.ADMIN)
        self.client.force_login(admin)
        self.client.post(reverse("set_language"), {"language": "uk", "next": "/"})

        self.client.post(
            reverse("fleet:car_create"),
            {**CAR_DATA, "price": "4150", "plate": "UA 0100 KK"},
        )

        car = Car.objects.get(plate="UA 0100 KK")
        self.assertEqual(car.price, Decimal("100.00"))

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
            reverse("fleet:car_add_photos", args=[car.pk]),
            {"photos": tiny_png()},
            follow=True,
        )
        self.assertContains(upload, "Added 1 photo")
        self.assertEqual(CarPhoto.objects.filter(car=car).count(), 1)

        self.client.post(reverse("fleet:car_delete", args=[car.pk]))
        self.assertFalse(Car.objects.filter(pk=car.pk).exists())
        self.assertFalse(CarPhoto.objects.filter(car_id=car.pk).exists())

    def test_admin_can_edit_a_car_and_delete_one_photo(self):
        admin = make_user("admin-edit@example.com", Role.ADMIN)
        self.client.force_login(admin)
        car = Car.objects.create(
            brand="Fiat",
            model="500",
            year=2019,
            price="30",
            plate="FT 500 KK",
            fuel="Gasoline",
            transmission="Manual",
            car_class="Economy",
        )
        self.client.post(reverse("fleet:car_add_photos", args=[car.pk]), {"photos": [tiny_png("one.png"), tiny_png("two.png")]})
        photos = list(CarPhoto.objects.filter(car=car))
        self.assertEqual(len(photos), 2)
        removed_path = photos[0].image.path

        updated = self.client.post(
            reverse("fleet:car_edit", args=[car.pk]),
            {
                "brand": "Fiat",
                "model": "500X",
                "year": 2021,
                "price": "42",
                "seats": 5,
                "plate": "FT 500 KK",
                "color": "Red",
                "transmission": "Automatic",
                "fuel": "Hybrid",
                "car_class": "Comfort",
                "mileage": 500,
                "description": "Updated",
            },
            follow=True,
        )
        car.refresh_from_db()
        self.assertEqual(car.model, "500X")
        self.assertEqual(car.car_class, "Comfort")
        self.assertContains(updated, "updated!")
        self.assertContains(updated, "Comfort")

        deleted = self.client.post(
            reverse("fleet:car_delete_photo", args=[car.pk, photos[0].pk]),
            follow=True,
        )
        self.assertContains(deleted, "Photo deleted")
        self.assertFalse(CarPhoto.objects.filter(pk=photos[0].pk).exists())
        self.assertTrue(CarPhoto.objects.filter(pk=photos[1].pk).exists())
        self.assertFalse(os.path.exists(removed_path))

    def test_client_cannot_edit_a_car_or_delete_a_photo(self):
        client = make_user("client-edit@example.com", Role.CLIENT)
        self.client.force_login(client)
        car = Car.objects.create(
            brand="Fiat",
            model="500",
            year=2019,
            price="30",
            plate="FT 501 KK",
            fuel="Gasoline",
            transmission="Manual",
        )
        photo = CarPhoto.objects.create(car=car, image=tiny_png())

        self.assertEqual(self.client.get(reverse("fleet:car_edit", args=[car.pk])).status_code, 403)
        self.assertEqual(
            self.client.post(reverse("fleet:car_delete_photo", args=[car.pk, photo.pk])).status_code,
            403,
        )
        self.assertTrue(CarPhoto.objects.filter(pk=photo.pk).exists())

    def test_add_car_link_is_only_shown_to_admins(self):
        admin = make_user("admin-link@example.com", Role.ADMIN)
        client = make_user("client-link@example.com", Role.CLIENT)

        self.client.force_login(admin)
        self.assertContains(self.client.get(reverse("fleet:catalog")), "Add Car")

        self.client.force_login(client)
        self.assertNotContains(self.client.get(reverse("fleet:catalog")), "Add Car")
