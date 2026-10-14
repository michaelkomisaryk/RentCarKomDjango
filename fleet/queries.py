from django.apps import apps
from django.db.models import Count, IntegerField, Q, Value


def annotate_availability(queryset):
    """Mark each car with how many active rentals it has.

    Availability is derived from rentals so it cannot drift from bookings.
    Before the rentals app exists, every car is treated as free.
    """
    if apps.is_installed("rentals"):
        return queryset.annotate(
            active_rental_count=Count(
                "rentals",
                filter=Q(rentals__status="active"),
            )
        )
    return queryset.annotate(
        active_rental_count=Value(0, output_field=IntegerField())
    )


def catalog_cars(fuel="All", available_only=False):
    from fleet.models import Car

    cars = annotate_availability(
        Car.objects.prefetch_related("photos").order_by("id")
    )
    if fuel and fuel != "All":
        cars = cars.filter(fuel=fuel)
    if available_only:
        cars = cars.filter(active_rental_count=0)
    return cars
