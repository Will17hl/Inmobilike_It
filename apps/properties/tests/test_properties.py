from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.accounts.models import AgentProfile
from apps.properties.forms import LocationForm, PropertyForm
from apps.properties.models import Location, Property
from apps.properties.services.property_service import PropertyService


class PropertyModelTest(TestCase):
    def test_create_property(self):
        location = Location.objects.create(
            city="City",
            neighborhood="Neigh",
            address="Addr",
        )
        property_obj = Property.objects.create(
            title="Apartamento de prueba",
            description="Descripcion de prueba",
            price=250000000,
            operation="sale",
            is_active=True,
            location=location,
        )

        self.assertEqual(property_obj.title, "Apartamento de prueba")
        self.assertEqual(property_obj.operation, "sale")
        self.assertTrue(property_obj.is_active)

    def test_property_precio_negativo_falla(self):
        location = Location.objects.create(city="City", neighborhood="Neigh", address="Addr")
        property_obj = Property(
            title="Apartamento con precio negativo",
            description="Descripcion de prueba",
            price=-1000,
            operation="sale",
            is_active=True,
            location=location,
        )
        with self.assertRaises(ValidationError):
            property_obj.full_clean()

    def test_create_property_survives_upload_storage_failure(self):
        user = get_user_model().objects.create_user(username="agent", password="secret")
        agent = AgentProfile.objects.create(user=user, phone="3001234567")
        loc_form = LocationForm(
            {
                "city": "Medellin",
                "neighborhood": "La Aguacatala",
                "address": "Calle 10 # 20-30",
            }
        )
        prop_form = PropertyForm(
            {
                "title": "Apartamento Familiar",
                "description": "Hermoso apto familiar en increible zona.",
                "operation": Property.OP_RENT,
                "price": "4000000",
                "bedrooms": "3",
                "bathrooms": "2",
                "area_m2": "80",
                "is_active": "on",
            }
        )
        image = SimpleUploadedFile("cover.jpg", b"not-a-real-image", content_type="image/jpeg")

        self.assertTrue(loc_form.is_valid(), loc_form.errors)
        self.assertTrue(prop_form.is_valid(), prop_form.errors)
        with patch("apps.properties.services.property_service.logger.exception"), patch(
            "apps.properties.services.property_service.PropertyImage.objects.create",
            side_effect=RuntimeError("storage unavailable"),
        ):
            property_obj = PropertyService.create_property(agent, loc_form, prop_form, files=[image])

        self.assertEqual(Property.objects.count(), 1)
        self.assertEqual(property_obj.images.count(), 0)
        self.assertTrue(property_obj.cover_display_url.startswith("https://images.unsplash.com/"))
