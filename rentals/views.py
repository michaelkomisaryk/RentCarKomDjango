from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import ListView

from accounts.mixins import StaffRoleRequiredMixin
from fleet.models import Car
from rentals.models import Rental
from rentals.services import RentalError, cancel_rental, complete_rental, create_rental


class RentCarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        if not request.user.profile_is_complete:
            messages.error(
                request,
                "Add your phone, RNOKPP, and driver license in your profile before renting.",
            )
            return redirect("profile")
        try:
            days = int(request.POST.get("days") or 0)
        except ValueError:
            days = 0
        try:
            rental = create_rental(car, request.user, days, request.user.name)
        except RentalError as exc:
            messages.error(request, str(exc))
            return redirect("car_detail", pk=car.pk)

        messages.success(
            request,
            (
                f"Rental confirmed. {rental.car_brand} {rental.car_model}, "
                f"plate {rental.car_plate}, renter {rental.renter_name}, "
                f"{rental.days} days, total ${rental.total_price}, id {rental.pk}."
            ),
        )
        return redirect("catalog")


class RentalListView(StaffRoleRequiredMixin, ListView):
    template_name = "rentals/rental_list.html"
    context_object_name = "rentals"

    def get_queryset(self):
        status = self.request.GET.get("status", "all")
        rentals = Rental.objects.select_related("car", "user")
        if status in Rental.Status.values:
            rentals = rentals.filter(status=status)
        return rentals

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.request.GET.get("status", "all")
        context["statuses"] = ["all", *Rental.Status.values]
        return context


class RentalActionView(StaffRoleRequiredMixin, View):
    action = ""

    def post(self, request, pk):
        rental = get_object_or_404(Rental, pk=pk)
        try:
            if self.action == "complete":
                complete_rental(rental)
                messages.success(request, "Rental completed")
            else:
                cancel_rental(rental)
                messages.success(request, "Rental cancelled")
        except RentalError as exc:
            messages.error(request, str(exc))
        return redirect(self._next_url(request))

    def _next_url(self, request):
        target = request.POST.get("next") or reverse("rental_list")
        if url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
            return target
        return reverse("rental_list")
