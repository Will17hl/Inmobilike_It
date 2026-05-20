from django.test import TestCase
from django.urls import reverse


class PropertiesReportsTest(TestCase):
    def test_pdf_report_endpoint(self):
        url = reverse('properties:properties_report_pdf')
        resp = self.client.get(url)
        # Puede devolver 200 (contenido) o 302 si requiere autenticación/redirección
        self.assertIn(resp.status_code, (200, 302))
        if resp.status_code == 200:
            self.assertEqual(resp['Content-Type'], 'application/pdf')

    def test_excel_report_endpoint(self):
        url = reverse('properties:properties_report_excel')
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (200, 302))
        if resp.status_code == 200:
            self.assertEqual(resp['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
