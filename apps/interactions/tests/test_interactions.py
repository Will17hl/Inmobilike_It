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

    def test_agregar_favorito_duplicado_no_crea_segundo_registro(self):
        favorite_service = FavoriteService()
        # Agregar la primera vez
        favorite_service.add_to_favorites(self.user, self.property_obj)
        self.assertEqual(Favorite.objects.count(), 1)
        
        # Intentar agregar por segunda vez
        favorite_service.add_to_favorites(self.user, self.property_obj)
        
        # Verificar que solo hay 1 registro en BD
        self.assertEqual(Favorite.objects.count(), 1)

    def test_usuario_no_autenticado_no_puede_enviar_inquiry(self):
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        # No iniciar sesión intencionalmente
        url = reverse('interactions:inquiry_create', args=[self.property_obj.id])
        
        # Realizar la petición POST
        response = client.post(url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Me interesa'
        })
        
        # Debe redirigir al login (302) porque ahora tiene @login_required
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))