from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse


class Rental(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    car = models.ForeignKey("fleet.Car", related_name="rentals", on_delete=models.PROTECT)
    car_brand = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    car_plate = models.CharField(max_length=32)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="rentals",
        on_delete=models.PROTECT,
    )
    user_email = models.EmailField()
    renter_name = models.CharField(max_length=150)
    renter_phone = models.CharField(max_length=20, blank=True)
    renter_rnokpp = models.CharField(max_length=10, blank=True)
    renter_license = models.CharField(max_length=16, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    days = models.PositiveIntegerField()
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "оренда"
        verbose_name_plural = "оренди"
        permissions = [("manage_rentals", "Може керувати орендами")]
        constraints = [
            models.UniqueConstraint(
                fields=["car"],
                condition=Q(status="active"),
                name="one_active_rental_per_car",
            )
        ]

    def __str__(self):
        return f"{self.car_brand} {self.car_model} ({self.status})"

    def get_absolute_url(self):
        return reverse("rentals:rental_detail", kwargs={"pk": self.pk})
