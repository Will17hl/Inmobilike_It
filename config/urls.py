from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

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
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)