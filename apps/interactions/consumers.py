import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        if self.user.is_anonymous:
            await self.close()
            return

        is_allowed = await self.user_in_conversation()
        if not is_allowed:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()

        if not message:
            return

        saved_message = await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": saved_message["content"],
                "sender": saved_message["sender"],
                "created_at": saved_message["created_at"],
                "sender_id": saved_message["sender_id"],
            }
        )

        await self.channel_layer.group_send(
            f"user_{saved_message['recipient_id']}_notifications",
            {
                "type": "notify_message",
                "message": saved_message["content"],
                "sender": saved_message["sender"],
                "created_at": saved_message["created_at"],
                "sender_id": saved_message["sender_id"],
                "conversation_id": saved_message["conversation_id"],
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "created_at": event["created_at"],
            "sender_id": event["sender_id"],
        }))

    @database_sync_to_async
    def user_in_conversation(self):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return self.user == conversation.buyer or self.user == conversation.advisor
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        conversation = Conversation.objects.get(id=self.conversation_id)
        msg = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content,
            is_read=False,
        )

        conversation.save()

        recipient = (
            conversation.advisor
            if self.user == conversation.buyer
            else conversation.buyer
        )

        return {
            "content": msg.content,
            "sender": self.user.username,
            "created_at": msg.created_at.strftime("%H:%M"),
            "sender_id": self.user.id,
            "recipient_id": recipient.id,
            "conversation_id": conversation.id,
        }


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{self.user.id}_notifications"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "created_at": event["created_at"],
            "sender_id": event["sender_id"],
            "conversation_id": event["conversation_id"],
        }))
