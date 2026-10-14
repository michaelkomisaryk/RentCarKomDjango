from fleet.models import Car
from rentals.models import Rental


def staff_stats(request):
    user = request.user
    if not user.is_authenticated or not getattr(user, "is_staff_role", False):
        return {}
    total = Car.objects.count()
    rented = Car.objects.filter(rentals__status=Rental.Status.ACTIVE).distinct().count()
    return {
        "stats": {
            "total_cars": total,
            "rented": rented,
            "available": total - rented,
            "all_rentals": Rental.objects.count(),
        }
    }
