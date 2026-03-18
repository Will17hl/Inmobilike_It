from django.contrib import admin
from .models import Favorite, Inquiry
from .models import Conversation, Message

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

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "buyer", "advisor", "updated_at")
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "created_at", "is_read")