from django.contrib import admin
from .models import Location, Property, PropertyImage

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