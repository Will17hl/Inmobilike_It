from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.http import Http404
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from apps.properties.services.property_service import PropertyService
from .forms import InquiryForm
from .services.favorite_service import FavoriteService
from .services.contact_service import ContactService
from .models import Conversation, Message

@login_required
def toggle_favorite(request, pk: int):
    prop = PropertyService.get_property_detail(pk)
    if not prop:
        raise Http404(_("Propiedad no encontrada"))

    favorite_service = FavoriteService()
    if favorite_service.is_favorite(request.user, prop):
        favorite_service.remove_from_favorites(request.user, prop)
    else:
        favorite_service.add_to_favorites(request.user, prop)

    return redirect("properties:detail", pk=pk)


@login_required
def inquiry_create(request, pk: int):
    prop = PropertyService.get_property_detail(pk)
    if not prop:
        raise Http404(_("Propiedad no encontrada"))

    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            contact_service = ContactService()
            contact_service.initiate_contact(
                property_obj=prop,
                user=request.user if request.user.is_authenticated else None,
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                message=form.cleaned_data["message"],
            )
            return render(
                request,
                "interactions/inquiry_success.html",
                {"prop": prop},
            )
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                "name": request.user.get_full_name(),
                "email": request.user.email,
            }
        form = InquiryForm(initial=initial_data)

    return render(
        request,
        "interactions/inquiry_form.html",
        {
            "form": form,
            "prop": prop,
        },
    )


@login_required
def clear_chat_notifications(request):
    if request.method != "POST":
        return JsonResponse({"detail": _("Método no permitido")}, status=405)

    updated = (
        Message.objects
        .filter(
            Q(conversation__buyer=request.user) | Q(conversation__advisor=request.user)
        )
        .exclude(sender=request.user)
        .filter(is_read=False)
        .update(is_read=True)
    )
    return JsonResponse({"ok": True, "updated": updated})


@login_required
def chat_dashboard(request, conversation_id=None):
    conversations = (
        Conversation.objects.select_related(
            "property__location",
            "buyer",
            "advisor",
        )
        .prefetch_related(
            Prefetch(
                "messages",
                queryset=Message.objects.select_related("sender").order_by("created_at"),
            ),
            "property__images",
        )
        .filter(Q(buyer=request.user) | Q(advisor=request.user))
        .distinct()
        .order_by("-updated_at")
    )

    active_conversation = None
    messages = []

    if conversation_id is not None:
        active_conversation = get_object_or_404(
            Conversation.objects.select_related(
                "property__location",
                "buyer",
                "advisor",
            ).prefetch_related("property__images"),
            id=conversation_id,
        )

        if request.user != active_conversation.buyer and request.user != active_conversation.advisor:
            messages.error(request, _("No tienes acceso a esa conversación."))
            return redirect("interactions:chat_list")

        messages = active_conversation.messages.select_related("sender")
        active_conversation.messages.exclude(sender=request.user).update(is_read=True)

    elif conversations:
        active_conversation = conversations.first()
        messages = active_conversation.messages.select_related("sender")
        active_conversation.messages.exclude(sender=request.user).update(is_read=True)

    conversations_data = []
    total_unread = 0

    for conversation in conversations:
        other_user = (
            conversation.advisor
            if request.user == conversation.buyer
            else conversation.buyer
        )

        property_obj = conversation.property

        last_message = conversation.messages.all().last()
        unread_count = (
            conversation.messages
            .exclude(sender=request.user)
            .filter(is_read=False)
            .count()
        )

        if active_conversation and conversation.id == active_conversation.id:
            unread_count = 0

        total_unread += unread_count

        conversations_data.append({
            "conversation": conversation,
            "other_user": other_user,
            "last_message": last_message,
            "unread_count": unread_count,
            "property_location": str(property_obj.location),
            "property_url": reverse("properties:detail", kwargs={"pk": property_obj.pk}),
            "cover_url": property_obj.cover_display_url,
        })

    active_chat_meta = None
    if active_conversation:
        active_property = active_conversation.property

        active_chat_meta = {
            "property_location": str(active_property.location),
            "property_url": reverse("properties:detail", kwargs={"pk": active_property.pk}),
            "cover_url": active_property.cover_display_url,
        }

    return render(request, "interactions/chat_dashboard.html", {
        "conversations_data": conversations_data,
        "active_conversation": active_conversation,
        "messages": messages,
        "total_unread": total_unread,
        "conversation_count": len(conversations_data),
        "active_chat_meta": active_chat_meta,
    })
