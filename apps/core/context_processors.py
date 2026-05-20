import json
from urllib import error as urlerror
from urllib import request as urlrequest

from django.utils.translation import gettext as _

OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=6.25&longitude=-75.58&current_weather=true"
)


def _fetch_medellin_weather():
    req = urlrequest.Request(OPEN_METEO_URL, headers={"User-Agent": "InmobilikeIt/1.0"})
    with urlrequest.urlopen(req, timeout=4) as response:
        payload = json.loads(response.read().decode("utf-8"))
    current = payload.get("current_weather") or {}
    temperature = current.get("temperature")
    if temperature is None:
        return None
    return {
        "city": _("Medellín"),
        "temperature": temperature,
        "windspeed": current.get("windspeed"),
    }


def weather_header(request):
    """Consume Open-Meteo (API externa) y expone el clima en el header."""
    try:
        weather = _fetch_medellin_weather()
    except (urlerror.URLError, urlerror.HTTPError, TimeoutError, ValueError, KeyError, json.JSONDecodeError):
        weather = None
    return {"header_weather": weather}
