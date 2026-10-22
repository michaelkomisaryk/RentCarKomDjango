from django.apps import apps
from django.conf import settings
from django.db import models
from django.urls import reverse


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
    is_featured = models.BooleanField(default=False)
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="favorite_cars",
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cars_added",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "автомобіль"
        verbose_name_plural = "автомобілі"

    def delete(self, *args, **kwargs):
        photos = list(self.photos.all())
        result = super().delete(*args, **kwargs)
        for photo in photos:
            if photo.image:
                photo.image.delete(save=False)
        return result

    def __str__(self):
        return f"{self.brand} {self.model}"

    def get_absolute_url(self):
        return reverse("fleet:car_detail", kwargs={"pk": self.pk})

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
        verbose_name = "фото автомобіля"
        verbose_name_plural = "фото автомобілів"

    def __str__(self):
        return f"Photo of {self.car}"

    def get_absolute_url(self):
        return reverse("fleet:photo_detail", kwargs={"pk": self.pk})


class Review(models.Model):
    car = models.ForeignKey(Car, related_name="reviews", on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    text = models.TextField()
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "відгук"
        verbose_name_plural = "відгуки"

    def __str__(self):
        return f"{self.rating}/5 · {self.car}"

    def get_absolute_url(self):
        return reverse("fleet:review_detail", kwargs={"pk": self.pk})
