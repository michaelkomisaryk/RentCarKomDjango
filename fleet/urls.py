from django.urls import path

from fleet.views import CarDetailView, CarListView

urlpatterns = [
    path("", CarListView.as_view(), name="catalog"),
    path("cars/<int:pk>/", CarDetailView.as_view(), name="car_detail"),
]
