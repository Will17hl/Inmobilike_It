from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

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
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
