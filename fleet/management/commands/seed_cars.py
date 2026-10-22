import sys
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from fleet.data.vehicles import RETIRED_PLATES, VEHICLES
from fleet.models import Car, CarPhoto
from fleet.photos import fetch_all, photo_path


class Command(BaseCommand):
    help = "Create or update the 40 demo cars and attach their three photographs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-download",
            action="store_true",
            help="Do not download photographs. Attach files that are already on disk.",
        )

    def handle(self, *args, **options):
        if not options["skip_download"] and "test" not in sys.argv:
            self.stdout.write("Looking for the three photographs of each car.")
            _, missing = fetch_all(stdout=self.stdout)
            if missing:
                self.stdout.write(self.style.WARNING(f"{len(missing)} photographs are still missing."))

        admin = User.objects.filter(email="admin@rentcarkom.com").first()
        created = updated = 0
        missing_photos = []
        with transaction.atomic():
            for spec in VEHICLES:
                _, was_created = _upsert(spec, admin)
                if was_created:
                    created += 1
                else:
                    updated += 1
            retired = _retire_unbooked()
        for spec in VEHICLES:
            car = Car.objects.get(plate=spec["plate"])
            if not _attach_photos(car, spec["slug"]):
                missing_photos.append(f"{spec['brand']} {spec['model']}")
        self.stdout.write(
            self.style.SUCCESS(
                f"Demo fleet ready ({created} created, {updated} updated, {retired} retired)."
            )
        )
        if missing_photos:
            self.stdout.write(self.style.WARNING("Cars still missing a full set of three photos:"))
            for name in missing_photos:
                self.stdout.write(f"  {name}")


def _upsert(spec, admin):
    fields = {
        "brand": spec["brand"],
        "model": spec["model"],
        "year": spec["year"],
        "price": spec["price"],
        "seats": spec["seats"],
        "transmission": spec["transmission"],
        "fuel": spec["fuel"],
        "car_class": spec["car_class"],
        "color": spec["color"],
        "mileage": spec["mileage"],
        "description": spec["description"],
    }
    car = Car.objects.filter(plate=spec["plate"]).first()
    if car is None:
        car = Car.objects.create(plate=spec["plate"], added_by=admin, **fields)
        return car, True
    for key, value in fields.items():
        setattr(car, key, value)
    car.save()
    return car, False


def _retire_unbooked():
    retired = 0
    for plate in RETIRED_PLATES:
        car = Car.objects.filter(plate=plate).first()
        if car is None or car.rentals.exists():
            continue
        car.delete()
        retired += 1
    return retired


def _attach_photos(car, slug):
    paths = [photo_path(slug, view) for view in ("front", "rear", "interior")]
    present = [path for path in paths if path.exists()]
    if not present:
        return False
    expected = [f"{slug}-{path.name}" for path in present]
    current = [Path(photo.image.name).name for photo in car.photos.all()]
    if current == expected:
        return len(present) == 3
    for photo in list(car.photos.all()):
        if photo.image:
            photo.image.delete(save=False)
        photo.delete()
    for path in present:
        with path.open("rb") as handle:
            photo = CarPhoto(car=car)
            photo.image.save(f"{slug}-{path.name}", File(handle), save=True)
    return car.photos.count() == 3
