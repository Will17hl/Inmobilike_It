from django.urls import path
from .views import healthz, home

urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("", home, name="home"),
]
