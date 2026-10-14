from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from fleet.models import Car
from rentals.models import Rental


class RentalError(Exception):
    pass


def rental_end(start, days):
    """Last inclusive day of the rental, at 23:59:59 in the local timezone."""
    local_start = timezone.localtime(start)
    end_date = local_start.date() + timedelta(days=days - 1)
    end_local = datetime.combine(end_date, time(23, 59, 59))
    return timezone.make_aware(end_local, timezone.get_current_timezone())


@transaction.atomic
def create_rental(car, user, days, renter_name):
    if days < 1:
        raise RentalError("Enter at least 1 day")
    name = (renter_name or "").strip()
    if not name:
        raise RentalError("Renter name is required")

    cars = Car.objects.all()
    if connection.features.has_select_for_update:
        cars = cars.select_for_update()
    locked = cars.get(pk=car.pk)
    if Rental.objects.filter(car=locked, status=Rental.Status.ACTIVE).exists():
        raise RentalError("Car is already rented")

    start = timezone.now()
    price = locked.price
    try:
        with transaction.atomic():
            return Rental.objects.create(
                car=locked,
                car_brand=locked.brand,
                car_model=locked.model,
                car_plate=locked.plate,
                user=user,
                user_email=user.email,
                renter_name=name,
                start_datetime=start,
                end_datetime=rental_end(start, days),
                days=days,
                price_per_day=price,
                total_price=(price * days).quantize(Decimal("0.01")),
                status=Rental.Status.ACTIVE,
            )
    except IntegrityError as exc:
        raise RentalError("Car is already rented") from exc


@transaction.atomic
def _set_status(rental, status, close_now):
    rentals = Rental.objects.all()
    if connection.features.has_select_for_update:
        rentals = rentals.select_for_update()
    locked = rentals.get(pk=rental.pk)
    if locked.status != Rental.Status.ACTIVE:
        raise RentalError("Only an active rental can be updated")
    locked.status = status
    fields = ["status"]
    if close_now:
        locked.end_datetime = timezone.now()
        fields.append("end_datetime")
    locked.save(update_fields=fields)
    return locked


def complete_rental(rental):
    return _set_status(rental, Rental.Status.COMPLETED, close_now=True)


def cancel_rental(rental):
    return _set_status(rental, Rental.Status.CANCELLED, close_now=False)
