from django.urls import path
from . import views

app_name = "properties"

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("mine/", views.my_properties, name="mine"),
    path("reservations/", views.my_reservations, name="my_reservations"),
    path("transactions/", views.my_transactions, name="my_transactions"),
    path("create/", views.property_create, name="create"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("<int:pk>/checkout/", views.create_checkout_session, name="checkout"),
    path("<int:pk>/payment/success/", views.payment_success, name="payment_success"),
    path("<int:pk>/payment/cancel/", views.payment_cancel, name="payment_cancel"),
    path("<int:pk>/", views.property_detail, name="detail"),
    path("<int:pk>/edit/", views.property_edit, name="edit"),
    path("<int:pk>/delete/", views.property_delete, name="delete"),
    path("contact/<int:pk>/", views.contact_advisor, name="contact_advisor"),
]
