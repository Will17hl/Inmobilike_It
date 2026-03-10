from django.contrib import admin
from .models import AgentProfile

@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "agency_name")
    search_fields = ("user__username", "user__email", "phone", "agency_name")