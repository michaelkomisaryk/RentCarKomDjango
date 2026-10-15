from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from accounts.forms import EmailLoginForm, ProfileForm, RegisterForm
from accounts.models import Role, User


class SignInView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailLoginForm
    redirect_authenticated_user = True


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        User.objects.create_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
            name=form.cleaned_data["name"],
            phone=form.cleaned_data["phone"],
            rnokpp=form.cleaned_data["rnokpp"],
            driver_license=form.cleaned_data["driver_license"],
            role=Role.CLIENT,
        )
        messages.success(self.request, "Registered! Please sign in.")
        return super().form_valid(form)


class SignOutView(LogoutView):
    pass


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rentals = self.request.user.rentals.select_related("car")
        context["form"] = kwargs.get("form") or ProfileForm(instance=self.request.user)
        context["active_rentals"] = rentals.filter(status="active")
        context["past_rentals"] = rentals.exclude(status="active")
        return context

    def post(self, request):
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved.")
            return redirect("profile")
        return self.render_to_response(self.get_context_data(form=form))
