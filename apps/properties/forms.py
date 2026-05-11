from decimal import Decimal

from django import forms
from django.utils.translation import get_language

from .models import PropertyImage
from .models import Property, Location
from .utils import normalize_decimal_input

INPUT_CLASSES = "w-full rounded-xl border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"


def current_language_is_english():
    return (get_language() or "").split("-")[0] == "en"

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["city", "neighborhood", "address"]
        widgets = {
            "city": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "neighborhood": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "address": forms.TextInput(attrs={"class": INPUT_CLASSES}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if current_language_is_english():
            self.fields["city"].label = "City"
            self.fields["neighborhood"].label = "Neighborhood"
            self.fields["address"].label = "Address"

class PropertyForm(forms.ModelForm):
    price = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASSES,
                "data-price-input": "true",
                "inputmode": "numeric",
                "autocomplete": "off",
                "placeholder": "Ej: 890.000.000",
            }
        )
    )

    def clean_price(self):
        value = self.cleaned_data.get("price")
        normalized = normalize_decimal_input(value)
        if not normalized:
            message = "Enter a valid price." if current_language_is_english() else "Ingresa un precio valido."
            raise forms.ValidationError(message)
        return Decimal(normalized)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if current_language_is_english():
            self.fields["title"].label = "Title"
            self.fields["description"].label = "Description"
            self.fields["operation"].label = "Operation"
            self.fields["operation"].choices = [("rent", "Rent"), ("sale", "Sale")]
            self.fields["price"].label = "Price"
            self.fields["bedrooms"].label = "Bedrooms"
            self.fields["bathrooms"].label = "Bathrooms"
            self.fields["area_m2"].label = "Area (m2)"
            self.fields["is_active"].label = "Active property"

    class Meta:
        model = Property
        # ✅ IMPORTANT: quitamos "location"
        fields = [
            "title",
            "description",
            "operation",
            "price",
            "bedrooms",
            "bathrooms",
            "area_m2",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "description": forms.Textarea(attrs={"class": INPUT_CLASSES, "rows": 4}),
            "operation": forms.Select(attrs={"class": INPUT_CLASSES}),
            "bedrooms": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "bathrooms": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "area_m2": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
        }
        
