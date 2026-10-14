from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from fleet.models import Car, Fuel
from fleet.queries import annotate_availability, catalog_cars


class CarListView(ListView):
    template_name = "fleet/catalog.html"
    context_object_name = "cars"

    def get_queryset(self):
        return catalog_cars(
            fuel=self.request.GET.get("fuel", "All"),
            available_only=self.request.GET.get("available") == "1",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fuel"] = self.request.GET.get("fuel", "All")
        context["available"] = self.request.GET.get("available") == "1"
        context["fuels"] = ["All", *Fuel.values]
        return context


class CarDetailView(DetailView):
    template_name = "fleet/car_detail.html"
    context_object_name = "car"

    def get_object(self, queryset=None):
        return get_object_or_404(
            annotate_availability(Car.objects.prefetch_related("photos")),
            pk=self.kwargs["pk"],
        )
