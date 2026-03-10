from django.contrib import admin
from .models import Favorite, Inquiry

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "property", "created_at")
    search_fields = ("user__username", "property__title")
    list_filter = ("created_at",)

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "email", "name", "created_at")
    search_fields = ("email", "name", "property__title")
    list_filter = ("created_at",)