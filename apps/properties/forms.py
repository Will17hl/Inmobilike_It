from django import forms
from .models import PropertyImage
from .models import Property, Location

INPUT_CLASSES = "w-full rounded-xl border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["city", "neighborhood", "address"]
        widgets = {
            "city": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "neighborhood": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "address": forms.TextInput(attrs={"class": INPUT_CLASSES}),
        }

class PropertyForm(forms.ModelForm):
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
            "price": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "bedrooms": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "bathrooms": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "area_m2": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
        }
        