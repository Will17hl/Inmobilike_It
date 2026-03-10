from django.urls import path
from . import views

app_name = "properties"

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("mine/", views.my_properties, name="mine"),
    path("create/", views.property_create, name="create"),
    path("<int:pk>/", views.property_detail, name="detail"),
    path("<int:pk>/edit/", views.property_edit, name="edit"),
    path("<int:pk>/delete/", views.property_delete, name="delete"),
]