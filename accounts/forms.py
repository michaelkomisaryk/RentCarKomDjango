from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from accounts.validators import normalize_driver_license, normalize_phone, normalize_rnokpp


class EmailLoginForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": _("Невірна електронна пошта або пароль."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Email")
        self.fields["username"].required = False
        self.fields["password"].required = False

    def clean(self):
        email = (self.data.get("username") or "").strip().lower()
        password = self.data.get("password") or ""
        if not email or not password:
            raise forms.ValidationError(_("Заповніть усі поля."))
        self.cleaned_data["username"] = email
        self.cleaned_data["password"] = password
        return super().clean()


class RegisterForm(forms.Form):
    name = forms.CharField(label=_("Full name"), required=False)
    email = forms.EmailField(label=_("Email"), required=False)
    phone = forms.CharField(label=_("Phone"), required=False)
    rnokpp = forms.CharField(label=_("RNOKPP"), required=False)
    driver_license = forms.CharField(
        label=_("Driver license series and number"),
        required=False,
        help_text=_("New plastic license: ВХА 123456. Old laminated license: КІА 654321."),
    )
    password = forms.CharField(label=_("Password"), required=False, widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        name = (self.data.get("name") or "").strip()
        email_raw = (self.data.get("email") or "").strip()
        phone_raw = (self.data.get("phone") or "").strip()
        rnokpp_raw = (self.data.get("rnokpp") or "").strip()
        license_raw = (self.data.get("driver_license") or "").strip()
        password = self.data.get("password") or ""
        if not all([name, email_raw, phone_raw, rnokpp_raw, license_raw, password]):
            raise forms.ValidationError(_("Заповніть усі поля."))
        if self.errors:
            return cleaned
        if len(password) < 6:
            raise forms.ValidationError(_("Пароль має містити щонайменше 6 символів."))
        email = email_raw.lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Ця електронна пошта вже зареєстрована."))
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
            "name": _("Name"),
            "phone": _("Phone"),
            "rnokpp": _("RNOKPP"),
            "driver_license": _("Driver license series and number"),
        }
        help_texts = {
            "driver_license": _("New plastic license: ВХА 123456. Old laminated license: КІА 654321."),
        }

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError(_("Ім’я не може бути порожнім."))
        return name

    def clean_phone(self):
        return normalize_phone(self.cleaned_data.get("phone"))

    def clean_rnokpp(self):
        return normalize_rnokpp(self.cleaned_data.get("rnokpp"))

    def clean_driver_license(self):
        return normalize_driver_license(self.cleaned_data.get("driver_license"))


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(label=_("Current password"), widget=forms.PasswordInput)
    new_password = forms.CharField(label=_("New password"), widget=forms.PasswordInput)
    confirm_password = forms.CharField(label=_("Confirm new password"), widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get("current_password") or ""
        if not self.user.check_password(current):
            raise forms.ValidationError(_("Поточний пароль невірний."))
        return current

    def clean(self):
        cleaned = super().clean()
        new_password = cleaned.get("new_password") or ""
        confirm_password = cleaned.get("confirm_password") or ""
        if new_password and len(new_password) < 6:
            self.add_error("new_password", _("Пароль має містити щонайменше 6 символів."))
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error("confirm_password", _("Паролі не збігаються."))
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data["new_password"])
        self.user.save(update_fields=["password"])
        return self.user
