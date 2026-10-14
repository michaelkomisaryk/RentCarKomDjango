from django import forms

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
            "mileage",
            "description",
        ]
        labels = {
            "price": "Price per day ($)",
            "plate": "License plate",
            "mileage": "Mileage (km)",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["seats"].required = False
        self.fields["mileage"].required = False
        self.fields["color"].required = False
        self.fields["description"].required = False
        self.fields["seats"].initial = 5
        self.fields["brand"].error_messages["required"] = "Brand is required"
        self.fields["model"].error_messages["required"] = "Model is required"
        self.fields["plate"].error_messages["required"] = "License plate is required"
        self.fields["year"].error_messages.update(
            {"required": "Valid year is required", "invalid": "Valid year is required"}
        )
        self.fields["price"].error_messages.update(
            {
                "required": "Valid price is required",
                "invalid": "Valid price is required",
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
            raise forms.ValidationError("Valid year is required")
        return year

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Valid price is required")
        return price

    def clean_seats(self):
        return self.cleaned_data.get("seats") or 5

    def clean_mileage(self):
        mileage = self.cleaned_data.get("mileage")
        return 0 if mileage is None else mileage
