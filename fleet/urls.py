from django.urls import path

from fleet.views import (
    CarCreateView,
    CarDeleteView,
    CarDetailView,
    CarListView,
    CarPhotoUploadView,
)

urlpatterns = [
    path("", CarListView.as_view(), name="catalog"),
    path("cars/<int:pk>/", CarDetailView.as_view(), name="car_detail"),
    path("fleet/cars/new/", CarCreateView.as_view(), name="car_create"),
    path("fleet/cars/<int:pk>/delete/", CarDeleteView.as_view(), name="car_delete"),
    path("fleet/cars/<int:pk>/photos/", CarPhotoUploadView.as_view(), name="car_add_photos"),
]
