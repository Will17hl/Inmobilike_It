from django.db.models import Q

from .models import Conversation


def chat_notifications(request):
    if not request.user.is_authenticated:
        return {
            "bell_notifications": [],
            "bell_notification_count": 0,
        }

    conversations = (
        Conversation.objects.select_related("buyer", "advisor")
        .prefetch_related("messages")
        .filter(Q(buyer=request.user) | Q(advisor=request.user))
        .filter(messages__is_read=False)
        .exclude(messages__sender=request.user)
        .distinct()
        .order_by("-updated_at")
    )

    notifications = []
    total_unread = 0

    for conversation in conversations[:10]:
        unread_messages = [
            message
            for message in conversation.messages.all()
            if message.sender_id != request.user.id and not message.is_read
        ]
        if not unread_messages:
            continue

        latest_unread = unread_messages[-1]
        sender = (
            conversation.advisor
            if request.user == conversation.buyer
            else conversation.buyer
        )

        notifications.append({
            "conversation_id": conversation.id,
            "sender": sender.username,
            "preview": latest_unread.content,
        })
        total_unread += len(unread_messages)

    return {
        "bell_notifications": notifications,
        "bell_notification_count": total_unread,
    }
