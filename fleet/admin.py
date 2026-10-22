from django.contrib import admin

from fleet.models import Car, CarPhoto, Review


class CarPhotoInline(admin.TabularInline):
    model = CarPhoto
    extra = 0


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("brand", "model", "year", "plate", "car_class", "fuel", "price")
    search_fields = ("brand", "model", "plate")
    inlines = [CarPhotoInline]


@admin.register(CarPhoto)
class CarPhotoAdmin(admin.ModelAdmin):
    list_display = ("car", "image", "created_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("car", "author", "rating", "created_at")
    search_fields = ("text", "car__brand", "car__model", "author__email")
