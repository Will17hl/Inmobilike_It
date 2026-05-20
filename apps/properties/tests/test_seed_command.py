from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.properties.models import Property


class SeedCommandTest(TestCase):
    def test_seed_creates_real_estate_sample_data(self):
        call_command("seed", locations=2, properties=3, images=2, seed=7, stdout=StringIO())

        properties = list(Property.objects.select_related("location").order_by("id"))

        self.assertEqual(len(properties), 3)
        for property_obj in properties:
            self.assertIn(property_obj.operation, {Property.OP_RENT, Property.OP_SALE})
            self.assertGreater(property_obj.bedrooms, 0)
            self.assertGreater(property_obj.bathrooms, 0)
            self.assertIsNotNone(property_obj.area_m2)
            self.assertIn(" en ", property_obj.title)
            self.assertIn(property_obj.location.neighborhood, property_obj.title)
            self.assertRegex(property_obj.description, r"habitacion(?:es)?")
            self.assertRegex(property_obj.description, r"bano(?:s)?")
            self.assertIn(property_obj.location.city, property_obj.description)
            self.assertEqual(property_obj.images.count(), 2)
            cover = property_obj.images.get(is_cover=True)
            self.assertTrue(cover.display_url.startswith("https://images.unsplash.com/"))

    def test_idempotent_seed_does_not_duplicate_sample_data(self):
        call_command("seed", locations=2, properties=3, images=2, seed=7, idempotent=True, stdout=StringIO())
        call_command("seed", locations=2, properties=3, images=2, seed=7, idempotent=True, stdout=StringIO())

        properties = Property.objects.prefetch_related("images")

        self.assertEqual(properties.count(), 3)
        for property_obj in properties:
            self.assertEqual(property_obj.images.count(), 2)
            self.assertEqual(property_obj.images.filter(is_cover=True).count(), 1)
