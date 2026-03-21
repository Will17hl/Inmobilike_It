from django.db import models
from django.utils import timezone
from apps.accounts.models import AgentProfile
from django.conf import settings


class Location(models.Model):
    city = models.CharField(max_length=80)
    neighborhood = models.CharField(max_length=120)
    address = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.neighborhood}, {self.city}"

class Property(models.Model):
    OP_RENT = "rent"
    OP_SALE = "sale"
    OP_CHOICES = [
        (OP_RENT, "Arriendo"),
        (OP_SALE, "Venta"),
    ]

    title = models.CharField(max_length=160)
    description = models.TextField()
    operation = models.CharField(max_length=10, choices=OP_CHOICES)
    price = models.DecimalField(max_digits=14, decimal_places=2)

    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    area_m2 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="properties")
    agent = models.ForeignKey(
        AgentProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="properties",
    )

    def __str__(self):
        return self.title

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="properties/", null=True, blank=True)
    image_url = models.URLField(blank=True)
    is_cover = models.BooleanField(default=False)

    def __str__(self):
        return f"Img #{self.id} of {self.property_id}"


class PropertyPayment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELED = "canceled"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendiente"),
        (STATUS_PAID, "Pagado"),
        (STATUS_CANCELED, "Cancelado"),
        (STATUS_FAILED, "Fallido"),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="property_payments",
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=10, default="cop")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    stripe_session_id = models.CharField(max_length=255, unique=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment #{self.id} - property {self.property_id} - {self.status}"
