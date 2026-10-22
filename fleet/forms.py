from django import forms
from django.utils.translation import gettext_lazy as _

from fleet.currency import uah_to_usd, usd_to_uah, uses_uah
from fleet.models import Car


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            "brand",
            "model",
            "year",
            "price",
            "seats",
            "plate",
            "color",
            "transmission",
            "fuel",
            "car_class",
            "mileage",
            "description",
            "is_featured",
        ]
        labels = {
            "brand": _("Brand"),
            "model": _("Model"),
            "year": _("Year"),
            "price": _("Price per day ($)"),
            "seats": _("Seats"),
            "plate": _("License plate"),
            "color": _("Color"),
            "transmission": _("Transmission"),
            "fuel": _("Fuel"),
            "car_class": _("Class"),
            "mileage": _("Mileage (km)"),
            "description": _("Description"),
            "is_featured": _("Featured"),
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if uses_uah():
            self.fields["price"].label = _("Price per day (UAH)")
            if not self.is_bound and self.instance.pk and self.instance.price is not None:
                self.initial["price"] = usd_to_uah(self.instance.price)
        self.fields["seats"].required = False
        self.fields["mileage"].required = False
        self.fields["color"].required = False
        self.fields["description"].required = False
        self.fields["seats"].initial = 5
        self.fields["brand"].error_messages["required"] = _("Brand is required")
        self.fields["model"].error_messages["required"] = _("Model is required")
        self.fields["plate"].error_messages["required"] = _("License plate is required")
        self.fields["year"].error_messages.update(
            {"required": _("Valid year is required"), "invalid": _("Valid year is required")}
        )
        self.fields["price"].error_messages.update(
            {
                "required": _("Valid price is required"),
                "invalid": _("Valid price is required"),
            }
        )

    def clean_brand(self):
        return self.cleaned_data["brand"].strip()

    def clean_model(self):
        return self.cleaned_data["model"].strip()

    def clean_plate(self):
        return self.cleaned_data["plate"].strip()

    def clean_year(self):
        year = self.cleaned_data["year"]
        if year < 1900 or year > 2100:
            raise forms.ValidationError(_("Valid year is required"))
        return year

    def clean_price(self):
        price = self.cleaned_data["price"]
        if uses_uah():
            price = uah_to_usd(price)
        if price <= 0:
            raise forms.ValidationError(_("Valid price is required"))
        return price

    def clean_seats(self):
        return self.cleaned_data.get("seats") or 5

    def clean_mileage(self):
        mileage = self.cleaned_data.get("mileage")
        return 0 if mileage is None else mileage
