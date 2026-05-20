from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, Mock


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