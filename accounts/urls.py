from django.urls import path

from accounts.views import ProfileView, RegisterView, SignInView, SignOutView

urlpatterns = [
    path("accounts/login/", SignInView.as_view(), name="login"),
    path("accounts/register/", RegisterView.as_view(), name="register"),
    path("accounts/logout/", SignOutView.as_view(), name="logout"),
    path("accounts/profile/", ProfileView.as_view(), name="profile"),
]
