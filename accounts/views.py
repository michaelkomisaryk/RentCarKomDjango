from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import FormView

from accounts.forms import EmailLoginForm, RegisterForm
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
            role=Role.CLIENT,
        )
        messages.success(self.request, "Registered! Please sign in.")
        return super().form_valid(form)


class SignOutView(LogoutView):
    pass
