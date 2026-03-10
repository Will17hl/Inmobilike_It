from django.conf import settings
from django.db import models

class AgentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="agent_profile",
    )
    phone = models.CharField(max_length=30)
    agency_name = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Asesor: {self.user.username}"