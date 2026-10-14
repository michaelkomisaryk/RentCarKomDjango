from django import forms
from django.contrib.auth.forms import AuthenticationForm

from accounts.models import User


class EmailLoginForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Invalid email or password",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"
        self.fields["username"].required = False
        self.fields["password"].required = False

    def clean(self):
        email = (self.data.get("username") or "").strip().lower()
        password = self.data.get("password") or ""
        if not email or not password:
            raise forms.ValidationError("Please fill in all fields")
        self.cleaned_data["username"] = email
        self.cleaned_data["password"] = password
        return super().clean()


class RegisterForm(forms.Form):
    name = forms.CharField(label="Full name", required=False)
    email = forms.EmailField(label="Email", required=False)
    password = forms.CharField(label="Password", required=False, widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        name = (self.data.get("name") or "").strip()
        email_raw = (self.data.get("email") or "").strip()
        password = self.data.get("password") or ""
        if not name or not email_raw or not password:
            raise forms.ValidationError("Please fill in all fields")
        if self.errors:
            return cleaned
        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters")
        email = email_raw.lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        cleaned["name"] = name
        cleaned["email"] = email
        cleaned["password"] = password
        return cleaned
