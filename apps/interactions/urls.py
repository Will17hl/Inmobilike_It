from django.urls import path
from .views import toggle_favorite, inquiry_create

app_name = "interactions"

urlpatterns = [
    path("p/<int:pk>/like/", toggle_favorite, name="toggle_favorite"),
    path("p/<int:pk>/inquiry/", inquiry_create, name="inquiry_create"),
]