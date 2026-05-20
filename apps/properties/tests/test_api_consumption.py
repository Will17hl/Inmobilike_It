from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch, Mock

from apps.properties.models import Location, Property, PropertyImage


@override_settings(SECURE_SSL_REDIRECT=False)
class ProductosAliadosViewTest(TestCase):
    def test_productos_aliados_renders_results_from_api(self):
        api_url = reverse('properties:api_properties_list')

        fake_payload = {
            'results': [
                {'id': 1, 'title': 'P1', 'description': 'Desc', 'price': '1000', 'operation': 'sale', 'city': 'C', 'neighborhood': 'N', 'cover_url': ''}
            ],
            'page': 1,
            'page_size': 10,
            'total_pages': 1,
            'total': 1,
        }

        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = fake_payload

        with patch('requests.get', return_value=mock_resp):
            resp = self.client.get(reverse('properties:productos_aliados'))
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, 'Productos aliados')
            self.assertContains(resp, 'P1')

    def test_properties_api_returns_cover_from_image_url(self):
        location = Location.objects.create(
            city="Medellin",
            neighborhood="Laureles",
            address="Calle 10 # 20-30",
        )
        property_obj = Property.objects.create(
            title="Apartamento con foto",
            description="Descripcion de prueba",
            price=2500000,
            operation=Property.OP_RENT,
            is_active=True,
            location=location,
        )
        PropertyImage.objects.create(
            property=property_obj,
            image_url="https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80",
            is_cover=True,
        )

        resp = self.client.get(reverse("properties:api_properties_list"), HTTP_HOST="localhost")

        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload["results"][0]["cover_url"], property_obj.images.first().display_url)

    def test_properties_api_normalizes_invalid_pagination(self):
        resp = self.client.get(
            reverse("properties:api_properties_list"),
            {"page": "bad", "page_size": "0"},
        )

        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload["page"], 1)
        self.assertEqual(payload["page_size"], 10)
