from django.db import transaction
from apps.interactions.repositories.inquiry_repository import InquiryRepository
from apps.interactions.models import Conversation, Message

class ContactService:
    def __init__(self, repository=None):
        self.repository = repository or InquiryRepository

    @transaction.atomic
    def initiate_contact(self, property_obj, user=None, name="", email="", message=""):
        inquiry_data = {
            "property": property_obj,
            "name": name,
            "email": email,
            "message": message,
        }

        if user and user.is_authenticated:
            inquiry_data["user"] = user

        inquiry = self.repository.create(**inquiry_data)
        
        conversation = None
        if user and user.is_authenticated and getattr(property_obj, 'agent', None) and property_obj.agent.user != user:
            conversation, created = Conversation.objects.get_or_create(
                property=property_obj,
                buyer=user,
                advisor=property_obj.agent.user
            )
            
            Message.objects.create(
                conversation=conversation,
                sender=user,
                content=message,
                is_read=False
            )
            
        return inquiry, conversation
