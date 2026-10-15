from django import forms
from django.contrib.auth.forms import AuthenticationForm

from accounts.models import User
from accounts.validators import normalize_driver_license, normalize_phone, normalize_rnokpp


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
    phone = forms.CharField(label="Phone", required=False)
    rnokpp = forms.CharField(label="RNOKPP", required=False)
    driver_license = forms.CharField(
        label="Driver license series and number",
        required=False,
        help_text="New plastic license: ВХА 123456. Old laminated license: КІА 654321.",
    )
    password = forms.CharField(label="Password", required=False, widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        name = (self.data.get("name") or "").strip()
        email_raw = (self.data.get("email") or "").strip()
        phone_raw = (self.data.get("phone") or "").strip()
        rnokpp_raw = (self.data.get("rnokpp") or "").strip()
        license_raw = (self.data.get("driver_license") or "").strip()
        password = self.data.get("password") or ""
        if not all([name, email_raw, phone_raw, rnokpp_raw, license_raw, password]):
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
        cleaned["phone"] = normalize_phone(phone_raw)
        cleaned["rnokpp"] = normalize_rnokpp(rnokpp_raw)
        cleaned["driver_license"] = normalize_driver_license(license_raw)
        cleaned["password"] = password
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "phone", "rnokpp", "driver_license")
        labels = {
            "phone": "Phone",
            "rnokpp": "RNOKPP",
            "driver_license": "Driver license series and number",
        }
        help_texts = {
            "driver_license": "New plastic license: ВХА 123456. Old laminated license: КІА 654321.",
        }

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Name cannot be empty")
        return name

    def clean_phone(self):
        return normalize_phone(self.cleaned_data.get("phone"))

    def clean_rnokpp(self):
        return normalize_rnokpp(self.cleaned_data.get("rnokpp"))

    def clean_driver_license(self):
        return normalize_driver_license(self.cleaned_data.get("driver_license"))
