from django.urls import path

from rentals.views import CancelOwnRentalView, RentalActionView, RentalListView, RentCarView

app_name = "rentals"

urlpatterns = [
    path("cars/<int:pk>/rent/", RentCarView.as_view(), name="rent_car"),
    path("rentals/", RentalListView.as_view(), name="rental_list"),
    path(
        "rentals/<int:pk>/complete/",
        RentalActionView.as_view(action="complete"),
        name="rental_complete",
    ),
    path(
        "rentals/<int:pk>/cancel/",
        RentalActionView.as_view(action="cancel"),
        name="rental_cancel",
    ),
    path(
        "rentals/<int:pk>/cancel-mine/",
        CancelOwnRentalView.as_view(),
        name="rental_cancel_own",
    ),
]
