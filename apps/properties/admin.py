from django.contrib import admin
from .models import Location, Property, PropertyImage, PropertyPayment

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "city", "neighborhood", "address")
    search_fields = ("city", "neighborhood", "address")

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "operation", "price", "is_active", "created_at", "location", "agent")
    list_filter = ("operation", "is_active", "location__city")
    search_fields = ("title", "description", "location__city", "location__neighborhood")
    inlines = [PropertyImageInline]

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "is_cover", "image", "image_url")
    list_filter = ("is_cover",)


@admin.register(PropertyPayment)
class PropertyPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "user", "amount", "currency", "status", "created_at", "paid_at")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("property__title", "user__username", "stripe_session_id", "stripe_payment_intent_id")
