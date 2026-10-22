from django.apps import apps
from django.conf import settings
from django.db import models


class Fuel(models.TextChoices):
    GASOLINE = "Gasoline", "Gasoline"
    DIESEL = "Diesel", "Diesel"
    HYBRID = "Hybrid", "Hybrid"
    ELECTRIC = "Electric", "Electric"


class Transmission(models.TextChoices):
    AUTOMATIC = "Automatic", "Automatic"
    MANUAL = "Manual", "Manual"


class CarClass(models.TextChoices):
    ECONOMY = "Economy", "Economy"
    COMFORT = "Comfort", "Comfort"
    PREMIUM = "Premium", "Premium"


class Car(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    seats = models.PositiveSmallIntegerField(default=5)
    transmission = models.CharField(
        max_length=20,
        choices=Transmission.choices,
        default=Transmission.AUTOMATIC,
    )
    fuel = models.CharField(max_length=20, choices=Fuel.choices, default=Fuel.GASOLINE)
    car_class = models.CharField(
        max_length=20,
        choices=CarClass.choices,
        default=CarClass.ECONOMY,
    )
    plate = models.CharField(max_length=32, unique=True)
    color = models.CharField(max_length=50, blank=True)
    mileage = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cars_added",
    )

    class Meta:
        ordering = ["id"]

    def delete(self, *args, **kwargs):
        photos = list(self.photos.all())
        result = super().delete(*args, **kwargs)
        for photo in photos:
            if photo.image:
                photo.image.delete(save=False)
        return result

    def __str__(self):
        return f"{self.brand} {self.model}"

    @property
    def is_rented(self):
        count = getattr(self, "active_rental_count", None)
        if count is not None:
            return count > 0
        if not apps.is_installed("rentals"):
            return False
        return self.rentals.filter(status="active").exists()


class CarPhoto(models.Model):
    car = models.ForeignKey(Car, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="cars/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Photo of {self.car}"
