from django.apps import apps
from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from accounts.mixins import AdminRequiredMixin
from fleet.forms import CarForm
from fleet.models import Car, CarPhoto, Fuel
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_rental"] = None
        context["my_rentals"] = []
        if not apps.is_installed("rentals"):
            return context
        rental_model = apps.get_model("rentals", "Rental")
        context["active_rental"] = rental_model.objects.filter(
            car=self.object,
            status="active",
        ).first()
        if self.request.user.is_authenticated:
            context["my_rentals"] = rental_model.objects.filter(
                car=self.object,
                user=self.request.user,
            )
        return context


class CarCreateView(AdminRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = "fleet/car_form.html"

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        response = super().form_valid(form)
        for image in self.request.FILES.getlist("photos"):
            if image:
                CarPhoto.objects.create(car=self.object, image=image)
        messages.success(
            self.request,
            f"Car '{self.object.brand} {self.object.model}' added!",
        )
        return response

    def get_success_url(self):
        return reverse("catalog")


class CarDeleteView(AdminRequiredMixin, DeleteView):
    model = Car
    template_name = "fleet/car_confirm_delete.html"
    success_url = reverse_lazy("catalog")

    def form_valid(self, form):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, "This car has rentals and cannot be deleted.")
            return redirect("car_detail", pk=self.object.pk)
        messages.success(self.request, "Car deleted")
        return redirect(success_url)


class CarPhotoUploadView(AdminRequiredMixin, View):
    def post(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        images = [image for image in request.FILES.getlist("photos") if image]
        if not images:
            messages.error(request, "Choose at least one photo")
            return redirect("car_detail", pk=car.pk)
        for image in images:
            CarPhoto.objects.create(car=car, image=image)
        messages.success(request, f"Added {len(images)} photo(s) successfully!")
        return redirect("car_detail", pk=car.pk)
