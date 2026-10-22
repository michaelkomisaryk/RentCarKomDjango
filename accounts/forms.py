from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from accounts.models import Role, User
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


class RegisterForm(UserCreationForm):
    error_messages = {
        **UserCreationForm.error_messages,
        "password_mismatch": _("Паролі не збігаються."),
    }
    name = forms.CharField(label=_("Full name"))
    email = forms.EmailField(label=_("Email"))
    phone = forms.CharField(label=_("Phone"))
    rnokpp = forms.CharField(label=_("RNOKPP"))
    driver_license = forms.CharField(
        label=_("Driver license series and number"),
        help_text=_("New plastic license: ВХА 123456. Old laminated license: КІА 654321."),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("name", "email", "phone", "rnokpp", "driver_license")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = _("Password")
        self.fields["password2"].label = _("Confirm new password")
        for field in self.fields.values():
            field.error_messages["required"] = _("Заповніть усі поля.")
        self.order_fields(
            ["name", "email", "phone", "rnokpp", "driver_license", "password1", "password2"]
        )

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError(_("Ім’я не може бути порожнім."))
        return name

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Ця електронна пошта вже зареєстрована."))
        return email

    def clean_phone(self):
        return normalize_phone(self.cleaned_data.get("phone"))

    def clean_rnokpp(self):
        return normalize_rnokpp(self.cleaned_data.get("rnokpp"))

    def clean_driver_license(self):
        return normalize_driver_license(self.cleaned_data.get("driver_license"))

    def clean_password1(self):
        password = self.cleaned_data.get("password1") or ""
        if len(password) < 6:
            raise forms.ValidationError(_("Пароль має містити щонайменше 6 символів."))
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = Role.CLIENT
        if commit:
            user.save()
        return user


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
