from django.urls import path
from .views import toggle_favorite, inquiry_create
from . import views

app_name = "interactions"

urlpatterns = [
    path("p/<int:pk>/like/", toggle_favorite, name="toggle_favorite"),
    path("p/<int:pk>/inquiry/", inquiry_create, name="inquiry_create"),
    path("notifications/clear/", views.clear_chat_notifications, name="clear_chat_notifications"),
    path("", views.chat_dashboard, name="chat_list"),
    path("<int:conversation_id>/", views.chat_dashboard, name="chat_room"),
]
