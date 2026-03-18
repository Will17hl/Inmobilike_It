from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from apps.properties.services.property_service import PropertyService
from .forms import InquiryForm
from .services.favorite_service import FavoriteService
from .services.inquiry_service import InquiryService
from .models import Conversation


@login_required
def toggle_favorite(request, pk: int):
    prop = PropertyService.get_property_detail(pk)
    if not prop:
        raise Http404("Property not found")

    if FavoriteService.is_favorite(request.user, prop):
        FavoriteService.remove_from_favorites(request.user, prop)
    else:
        FavoriteService.add_to_favorites(request.user, prop)

    return redirect("properties:detail", pk=pk)


def inquiry_create(request, pk: int):
    prop = PropertyService.get_property_detail(pk)
    if not prop:
        raise Http404("Property not found")

    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            InquiryService.create_inquiry(
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
def chat_dashboard(request, conversation_id=None):
    conversations = (
        Conversation.objects.filter(buyer=request.user)
        | Conversation.objects.filter(advisor=request.user)
    ).distinct().order_by("-updated_at")

    conversations_data = []

    for conversation in conversations:
        other_user = (
            conversation.advisor
            if request.user == conversation.buyer
            else conversation.buyer
        )

        last_message = conversation.messages.order_by("-created_at").first()
        unread_count = (
            conversation.messages
            .exclude(sender=request.user)
            .filter(is_read=False)
            .count()
        )

        conversations_data.append({
            "conversation": conversation,
            "other_user": other_user,
            "last_message": last_message,
            "unread_count": unread_count,
        })

    active_conversation = None
    messages = []

    if conversation_id is not None:
        active_conversation = get_object_or_404(Conversation, id=conversation_id)

        if request.user != active_conversation.buyer and request.user != active_conversation.advisor:
            return render(request, "core/403.html", status=403)

        messages = active_conversation.messages.select_related("sender")
        active_conversation.messages.exclude(sender=request.user).update(is_read=True)

    elif conversations:
        active_conversation = conversations.first()
        messages = active_conversation.messages.select_related("sender")
        active_conversation.messages.exclude(sender=request.user).update(is_read=True)

    return render(request, "interactions/chat_dashboard.html", {
        "conversations_data": conversations_data,
        "active_conversation": active_conversation,
        "messages": messages,
    })