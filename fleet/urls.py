from django.urls import path

from fleet.views import (
    CarCreateView,
    CarDeleteView,
    CarDetailView,
    CarListView,
    CarPhotoDeleteView,
    CarPhotoDetailView,
    CarPhotoListView,
    CarPhotoUploadView,
    CarUpdateView,
    ReviewDetailView,
    ReviewListView,
    fleet_summary,
)

app_name = "fleet"

urlpatterns = [
    path("", CarListView.as_view(), name="catalog"),
    path("cars/<int:pk>/", CarDetailView.as_view(), name="car_detail"),
    path("fleet/cars/new/", CarCreateView.as_view(), name="car_create"),
    path("fleet/cars/<int:pk>/edit/", CarUpdateView.as_view(), name="car_edit"),
    path("fleet/cars/<int:pk>/delete/", CarDeleteView.as_view(), name="car_delete"),
    path("fleet/cars/<int:pk>/photos/", CarPhotoUploadView.as_view(), name="car_add_photos"),
    path(
        "fleet/cars/<int:pk>/photos/<int:photo_pk>/delete/",
        CarPhotoDeleteView.as_view(),
        name="car_delete_photo",
    ),
    path("fleet/summary/", fleet_summary, name="summary"),
    path("fleet/photos/", CarPhotoListView.as_view(), name="photo_list"),
    path("fleet/photos/<int:pk>/", CarPhotoDetailView.as_view(), name="photo_detail"),
    path("fleet/reviews/", ReviewListView.as_view(), name="review_list"),
    path("fleet/reviews/<int:pk>/", ReviewDetailView.as_view(), name="review_detail"),
]
