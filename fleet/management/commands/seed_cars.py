from decimal import Decimal

from django.core.management.base import BaseCommand

from accounts.models import User
from fleet.models import Car

DEMO_CARS = (
    {
        "brand": "Toyota",
        "model": "Camry",
        "year": 2022,
        "price": Decimal("45"),
        "seats": 5,
        "transmission": "Automatic",
        "fuel": "Gasoline",
        "plate": "AA 1234 KK",
        "color": "White",
        "mileage": 32000,
        "description": "Comfortable mid-size sedan, perfect for city and highway driving.",
    },
    {
        "brand": "BMW",
        "model": "3 Series",
        "year": 2023,
        "price": Decimal("95"),
        "seats": 5,
        "transmission": "Automatic",
        "fuel": "Gasoline",
        "plate": "BB 5678 KK",
        "color": "Black",
        "mileage": 12000,
        "description": "Premium executive sedan with sporty handling and luxury interior.",
    },
    {
        "brand": "Ford",
        "model": "Explorer",
        "year": 2022,
        "price": Decimal("75"),
        "seats": 7,
        "transmission": "Automatic",
        "fuel": "Gasoline",
        "plate": "CC 9012 KK",
        "color": "Silver",
        "mileage": 28000,
        "description": "Spacious SUV ideal for family trips and off-road adventures.",
    },
    {
        "brand": "Mercedes",
        "model": "E-Class",
        "year": 2023,
        "price": Decimal("110"),
        "seats": 5,
        "transmission": "Automatic",
        "fuel": "Diesel",
        "plate": "DD 3456 KK",
        "color": "Gray",
        "mileage": 8000,
        "description": "Elegant luxury sedan with cutting-edge technology and supreme comfort.",
    },
    {
        "brand": "Volkswagen",
        "model": "Passat",
        "year": 2021,
        "price": Decimal("50"),
        "seats": 5,
        "transmission": "Manual",
        "fuel": "Diesel",
        "plate": "EE 7890 KK",
        "color": "Blue",
        "mileage": 55000,
        "description": "Reliable and fuel-efficient family sedan with generous trunk space.",
    },
    {
        "brand": "Hyundai",
        "model": "Tucson",
        "year": 2023,
        "price": Decimal("60"),
        "seats": 5,
        "transmission": "Automatic",
        "fuel": "Hybrid",
        "plate": "FF 1122 KK",
        "color": "Red",
        "mileage": 15000,
        "description": "Modern compact SUV with advanced safety features and hybrid efficiency.",
    },
    {
        "brand": "Audi",
        "model": "A4",
        "year": 2022,
        "price": Decimal("88"),
        "seats": 5,
        "transmission": "Automatic",
        "fuel": "Gasoline",
        "plate": "GG 3344 KK",
        "color": "Dark Blue",
        "mileage": 21000,
        "description": "Sporty premium sedan with quattro all-wheel drive and refined interior.",
    },
    {
        "brand": "Kia",
        "model": "Sportage",
        "year": 2023,
        "price": Decimal("55"),
        "seats": 5,
        "transmission": "Automatic",
        "fuel": "Hybrid",
        "plate": "HH 5566 KK",
        "color": "Green",
        "mileage": 9000,
        "description": "Stylish and practical crossover with great value and modern tech.",
    },
)


class Command(BaseCommand):
    help = "Create the eight demo cars from the original app."

    def handle(self, *args, **options):
        added_by = User.objects.filter(email="admin@rentcarkom.com").first()
        created_count = 0
        for data in DEMO_CARS:
            _, created = Car.objects.get_or_create(
                plate=data["plate"],
                defaults={**data, "added_by": added_by},
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"Demo cars ready ({created_count} created)."))
