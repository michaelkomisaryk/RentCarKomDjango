from django.contrib import admin

from fleet.models import Car, CarPhoto


class CarPhotoInline(admin.TabularInline):
    model = CarPhoto
    extra = 0


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("brand", "model", "year", "plate", "fuel", "price")
    search_fields = ("brand", "model", "plate")
    inlines = [CarPhotoInline]


@admin.register(CarPhoto)
class CarPhotoAdmin(admin.ModelAdmin):
    list_display = ("car", "image", "created_at")
