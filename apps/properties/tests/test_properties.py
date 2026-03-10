from django.test import TestCase
from apps.properties.models import Property


class PropertyModelTest(TestCase):
    def test_create_property(self):
        property_obj = Property.objects.create(
            title="Apartamento de prueba",
            description="Descripción de prueba",
            price=250000000,
            operation="sale",
            is_active=True
        )

        self.assertEqual(property_obj.title, "Apartamento de prueba")
        self.assertEqual(property_obj.operation, "sale")
        self.assertTrue(property_obj.is_active)