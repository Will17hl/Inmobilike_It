from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.interactions.models import Favorite
from apps.interactions.services.favorite_service import FavoriteService
from apps.properties.models import Property, Location

User = get_user_model()


class FavoriteServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="12345678"
        )

        self.location = Location.objects.create(
            city="Medellín",
            neighborhood="El Poblado",
            address="Calle 10"
        )

        self.property_obj = Property.objects.create(
            title="Apartamento prueba",
            description="Desc",
            operation="sale",
            price=300000000,
            is_active=True,
            location=self.location
        )

    def test_add_to_favorites(self):
        favorite_service = FavoriteService()
        favorite, created = favorite_service.add_to_favorites(self.user, self.property_obj)
        self.assertTrue(created)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_is_favorite(self):
        favorite_service = FavoriteService()
        Favorite.objects.create(user=self.user, property=self.property_obj)
        self.assertTrue(favorite_service.is_favorite(self.user, self.property_obj))