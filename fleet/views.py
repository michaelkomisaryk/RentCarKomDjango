from django.apps import apps
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.db.models import Avg, Count, ProtectedError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.mixins import AdminRequiredMixin
from fleet.forms import CarForm
from fleet.models import Car, CarClass, CarPhoto, Fuel, Review, Transmission
from fleet.queries import annotate_availability, catalog_cars


class CarListView(ListView):
    template_name = "fleet/catalog.html"
    context_object_name = "cars"
    paginate_by = 12

    def get_queryset(self):
        return catalog_cars(
            fuel=self.request.GET.get("fuel", "All"),
            car_class=self.request.GET.get("class", "All"),
            transmission=self.request.GET.get("transmission", "All"),
            seats=_seats(self.request.GET.get("seats")),
            query=self.request.GET.get("q", ""),
            available_only=self.request.GET.get("available") == "1",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fuel"] = self.request.GET.get("fuel", "All")
        context["car_class"] = self.request.GET.get("class", "All")
        context["transmission"] = self.request.GET.get("transmission", "All")
        context["seats"] = self.request.GET.get("seats") or "All"
        context["query"] = self.request.GET.get("q", "")
        context["available"] = self.request.GET.get("available") == "1"
        context["fuels"] = ["All", *Fuel.values]
        context["classes"] = ["All", *CarClass.values]
        context["transmissions"] = ["All", *Transmission.values]
        context["seat_choices"] = ["All", "4", "5", "7"]
        return context


def _seats(value):
    if not value or value == "All":
        return None
    try:
        return int(value)
    except ValueError:
        return None


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
            _("Car '%(brand)s %(model)s' added!")
            % {"brand": self.object.brand, "model": self.object.model},
        )
        return response

    def get_success_url(self):
        return reverse("fleet:catalog")


class CarUpdateView(AdminRequiredMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = "fleet/car_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in self.request.FILES.getlist("photos"):
            if image:
                CarPhoto.objects.create(car=self.object, image=image)
        messages.success(
            self.request,
            _("Car '%(brand)s %(model)s' updated!")
            % {"brand": self.object.brand, "model": self.object.model},
        )
        return response

    def get_success_url(self):
        return reverse("fleet:car_detail", kwargs={"pk": self.object.pk})


class CarDeleteView(AdminRequiredMixin, DeleteView):
    model = Car
    template_name = "fleet/car_confirm_delete.html"
    success_url = reverse_lazy("fleet:catalog")

    def form_valid(self, form):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, _("Це авто має оренди, тому його не можна видалити."))
            return redirect("fleet:car_detail", pk=self.object.pk)
        messages.success(self.request, _("Car deleted"))
        return redirect(success_url)


class CarPhotoUploadView(AdminRequiredMixin, View):
    def post(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        images = [image for image in request.FILES.getlist("photos") if image]
        if not images:
            messages.error(request, _("Оберіть хоча б одне фото."))
            return redirect("fleet:car_detail", pk=car.pk)
        for image in images:
            CarPhoto.objects.create(car=car, image=image)
        messages.success(
            request,
            ngettext(
                "Added %(count)s photo successfully!",
                "Added %(count)s photos successfully!",
                len(images),
            )
            % {"count": len(images)},
        )
        return redirect("fleet:car_detail", pk=car.pk)


class CarPhotoDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk, photo_pk):
        photo = get_object_or_404(CarPhoto, pk=photo_pk, car_id=pk)
        if photo.image:
            photo.image.delete(save=False)
        photo.delete()
        messages.success(request, _("Photo deleted"))
        target = request.POST.get("next") or reverse("fleet:car_detail", kwargs={"pk": pk})
        if url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
            return redirect(target)
        return redirect("fleet:car_detail", pk=pk)


def fleet_summary(request):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    if not request.user.is_staff_role:
        return HttpResponseForbidden()
    summary = Car.objects.aggregate(total=Count("id"), average_price=Avg("price"))
    if summary["average_price"] is None:
        summary["average_price"] = 0
    return render(request, "fleet/summary.html", {"summary": summary})


class CarPhotoListView(ListView):
    model = CarPhoto
    template_name = "fleet/photo_list.html"
    context_object_name = "photos"
    paginate_by = 12

    def get_queryset(self):
        return CarPhoto.objects.select_related("car").order_by("-created_at")


class CarPhotoDetailView(DetailView):
    model = CarPhoto
    template_name = "fleet/photo_detail.html"
    context_object_name = "photo"

    def get_queryset(self):
        return CarPhoto.objects.select_related("car")


class ReviewListView(ListView):
    model = Review
    template_name = "fleet/review_list.html"
    context_object_name = "reviews"
    paginate_by = 10

    def get_queryset(self):
        return Review.objects.select_related("car", "author")


class ReviewDetailView(DetailView):
    model = Review
    template_name = "fleet/review_detail.html"
    context_object_name = "review"

    def get_queryset(self):
        return Review.objects.select_related("car", "author")
