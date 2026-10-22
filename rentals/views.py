from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import ListView

from fleet.currency import format_money

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
                _("Add your phone, RNOKPP, and driver license in your profile before renting."),
            )
            return redirect("accounts:profile")
        try:
            days = int(request.POST.get("days") or 0)
        except ValueError:
            days = 0
        try:
            rental = create_rental(car, request.user, days, request.user.name)
        except RentalError as exc:
            messages.error(request, str(exc))
            return redirect("fleet:car_detail", pk=car.pk)

        messages.success(
            request,
            _(
                "Rental confirmed. %(brand)s %(model)s, plate %(plate)s, "
                "renter %(name)s, %(days)s days, total %(total)s, id %(id)s."
            )
            % {
                "brand": rental.car_brand,
                "model": rental.car_model,
                "plate": rental.car_plate,
                "name": rental.renter_name,
                "days": rental.days,
                "total": format_money(rental.total_price),
                "id": rental.pk,
            },
        )
        return redirect("fleet:catalog")


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


class CancelOwnRentalView(LoginRequiredMixin, View):
    def post(self, request, pk):
        rental = get_object_or_404(Rental, pk=pk, user=request.user)
        try:
            cancel_rental(rental)
        except RentalError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, _("Rental cancelled"))
        return redirect("accounts:profile")


class RentalActionView(StaffRoleRequiredMixin, View):
    action = ""

    def post(self, request, pk):
        rental = get_object_or_404(Rental, pk=pk)
        try:
            if self.action == "complete":
                complete_rental(rental)
                messages.success(request, _("Rental completed"))
            else:
                cancel_rental(rental)
                messages.success(request, _("Rental cancelled"))
        except RentalError as exc:
            messages.error(request, str(exc))
        return redirect(self._next_url(request))

    def _next_url(self, request):
        target = request.POST.get("next") or reverse("rentals:rental_list")
        if url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
            return target
        return reverse("rentals:rental_list")
