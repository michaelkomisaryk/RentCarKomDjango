from django.core.management import call_command
from django.test import TestCase

from fleet.models import Car


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
