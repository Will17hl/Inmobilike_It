from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from apps.core.context_processors import weather_header


class WeatherHeaderContextProcessorTest(SimpleTestCase):
    @patch("apps.core.context_processors._fetch_medellin_weather")
    def test_weather_header_exposes_temperature(self, mock_fetch):
        mock_fetch.return_value = {"city": "Medellín", "temperature": 24.5, "windspeed": 8.0}
        request = RequestFactory().get("/")
        context = weather_header(request)
        self.assertEqual(context["header_weather"]["temperature"], 24.5)
