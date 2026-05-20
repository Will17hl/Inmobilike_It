from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView
from django.conf.urls.static import static

from apps.properties.api import properties_list_api
from apps.properties.views import productos_aliados

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),

    # Rutas de la rúbrica (también disponibles bajo /properties/...)
    path("api/properties/", properties_list_api, name="api_properties_list_root"),
    path("productos-aliados/", productos_aliados, name="productos_aliados_root"),

    # Home
    path("", include("apps.core.urls")),

    # Accounts
    path("accounts/", include(("apps.accounts.urls", "accounts"), namespace="accounts")),

    # Properties
    path("properties/", include(("apps.properties.urls", "properties"), namespace="properties")),

    # Interactions
    path("interactions/", include(("apps.interactions.urls", "interactions"), namespace="interactions")),

    # Legacy chat URLs redirect to the canonical interactions routes.
    path("chats/", RedirectView.as_view(pattern_name="interactions:chat_list", permanent=False)),
    path("chats/<int:conversation_id>/", RedirectView.as_view(pattern_name="interactions:chat_room", permanent=False)),
]

if settings.DEBUG and settings.MEDIA_URL and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
