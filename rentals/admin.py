from django.contrib import admin

from rentals.models import Rental


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ("id", "car_brand", "car_model", "renter_name", "status", "total_price")
    list_filter = ("status",)
