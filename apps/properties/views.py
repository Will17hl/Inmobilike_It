from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from apps.interactions.models import Conversation, Message
from apps.accounts.models import AgentProfile
from apps.interactions.models import Favorite
from .forms import PropertyForm, LocationForm
from .services.property_service import PropertyService
from .models import Property, PropertyImage, PropertyPayment
from decimal import Decimal

import stripe


def sync_payment_from_checkout_session(payment, checkout_session):
    payment.stripe_payment_intent_id = checkout_session.payment_intent or ""

    if checkout_session.payment_status == "paid":
        payment.status = PropertyPayment.STATUS_PAID
        if payment.paid_at is None:
            payment.paid_at = timezone.now()
    elif checkout_session.status == "expired":
        payment.status = PropertyPayment.STATUS_FAILED
    else:
        payment.status = PropertyPayment.STATUS_PENDING

    payment.save(update_fields=["stripe_payment_intent_id", "status", "paid_at"])

def require_host(request):
    return request.session.get("mode", "guest") == "host"


def build_payment_summary(payments, include_buyer=False):
    items = []
    total_amount = Decimal("0.00")

    for payment in payments:
        property_obj = payment.property
        cover = property_obj.images.filter(is_cover=True).first() or property_obj.images.first()
        total_amount += payment.amount
        item = {
            "payment": payment,
            "property": property_obj,
            "cover": cover,
        }
        if include_buyer:
            item["buyer"] = payment.user
        items.append(item)

    return items, total_amount


def property_detail(request, pk: int):
    prop = PropertyService.get_property_detail(pk)
    if not prop:
        raise Http404("Property not found")

    is_fav = False
    can_edit = False

    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, property=prop).exists()

        if require_host(request):
            agent = AgentProfile.objects.filter(user=request.user).first()
            if agent and prop.agent_id == agent.id:
                can_edit = True

    cover = PropertyService.get_cover_image(prop)
    images = PropertyService.get_property_images(prop)

    return render(
        request,
        "properties/detail.html",
        {
            "prop": prop,
            "is_fav": is_fav,
            "cover": cover,
            "images": images,
            "can_edit": can_edit,
            "stripe_enabled": bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_PUBLISHABLE_KEY),
            "currency": settings.STRIPE_CURRENCY.upper(),
        },
    )


def catalog(request):
    city = request.GET.get("city", "").strip()
    neighborhood = request.GET.get("neighborhood", "").strip()
    operation = request.GET.get("operation", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    filters = {
        "city": city,
        "neighborhood": neighborhood,
        "operation": operation,
        "min_price": min_price,
        "max_price": max_price,
    }

    properties = PropertyService.list_active_properties(filters=filters)

    return render(
        request,
        "properties/catalog.html",
        {
            "properties": properties,
        },
    )
    
@login_required
def my_properties(request):
    if not require_host(request):
        return redirect("accounts:toggle_mode")

    agent, _ = AgentProfile.objects.get_or_create(user=request.user)
    properties = PropertyService.get_agent_properties(agent)

    return render(
        request,
        "properties/my_properties.html",
        {"properties": properties},
    )


@login_required
def my_reservations(request):
    reservations = (
        PropertyPayment.objects.filter(
            user=request.user,
            status=PropertyPayment.STATUS_PAID,
        )
        .select_related("property__location", "property__agent__user", "user")
        .prefetch_related("property__images")
        .order_by("-paid_at", "-created_at")
    )

    reservation_items, total_spent = build_payment_summary(reservations)

    return render(
        request,
        "properties/my_reservations.html",
        {
            "reservation_items": reservation_items,
            "reservation_count": reservations.count(),
            "total_spent": total_spent,
        },
    )


@login_required
def my_transactions(request):
    if not require_host(request):
        messages.info(request, "Activa el modo anfitrion para ver tus ventas y arriendos.")
        return redirect(f"{reverse('accounts:toggle_mode')}?next={request.path}")

    transactions = (
        PropertyPayment.objects.filter(
            property__agent__user=request.user,
            status=PropertyPayment.STATUS_PAID,
        )
        .select_related("property__location", "property__agent__user", "user")
        .prefetch_related("property__images")
        .order_by("-paid_at", "-created_at")
    )

    transaction_items, total_revenue = build_payment_summary(transactions, include_buyer=True)
    sale_count = transactions.filter(property__operation=Property.OP_SALE).count()
    rent_count = transactions.filter(property__operation=Property.OP_RENT).count()

    return render(
        request,
        "properties/my_transactions.html",
        {
            "transaction_items": transaction_items,
            "transaction_count": transactions.count(),
            "total_revenue": total_revenue,
            "sale_count": sale_count,
            "rent_count": rent_count,
        },
    )


@login_required
def property_create(request):
    if not require_host(request):
        return redirect("accounts:toggle_mode")

    agent, _ = AgentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        loc_form = LocationForm(request.POST, prefix="loc")
        prop_form = PropertyForm(request.POST, prefix="prop")

        if loc_form.is_valid() and prop_form.is_valid():
            prop = PropertyService.create_property(
                agent=agent,
                location_form=loc_form,
                property_form=prop_form,
                files=request.FILES.getlist("images"),
            )
            return redirect("properties:detail", pk=prop.pk)

        return render(
            request,
            "properties/property_create.html",
            {
                "loc_form": loc_form,
                "prop_form": prop_form,
            },
        )

    loc_form = LocationForm(prefix="loc")
    prop_form = PropertyForm(prefix="prop")

    return render(
        request,
        "properties/property_create.html",
        {
            "loc_form": loc_form,
            "prop_form": prop_form,
        },
    )


@login_required
def property_edit(request, pk: int):
    if not require_host(request):
        return redirect("accounts:toggle_mode")

    agent, _ = AgentProfile.objects.get_or_create(user=request.user)

    prop = Property.objects.select_related("location", "agent").prefetch_related("images").filter(pk=pk).first()
    if not prop:
        raise Http404("Property not found")

    if prop.agent_id != agent.id:
        raise Http404("You do not have permission to edit this property")

    if request.method == "POST":
        loc_form = LocationForm(request.POST, instance=prop.location, prefix="loc")
        prop_form = PropertyForm(request.POST, instance=prop, prefix="prop")

        if loc_form.is_valid() and prop_form.is_valid():
            loc_form.save()
            prop_form.save()

            delete_ids = request.POST.getlist("delete_images")
            if delete_ids:
                PropertyImage.objects.filter(property=prop, id__in=delete_ids).delete()

            new_images = request.FILES.getlist("images")
            created_images = []
            for img in new_images:
                created_images.append(
                    PropertyImage.objects.create(
                        property=prop,
                        image=img,
                        is_cover=False,
                    )
                )

            selected_cover_id = request.POST.get("cover_image")
            if selected_cover_id:
                PropertyImage.objects.filter(property=prop).update(is_cover=False)
                PropertyImage.objects.filter(property=prop, id=selected_cover_id).update(is_cover=True)
            else:
                remaining_images = prop.images.all()
                if remaining_images.exists() and not remaining_images.filter(is_cover=True).exists():
                    first_img = remaining_images.first()
                    first_img.is_cover = True
                    first_img.save(update_fields=["is_cover"])

            return redirect("properties:detail", pk=prop.pk)

    else:
        loc_form = LocationForm(instance=prop.location, prefix="loc")
        prop_form = PropertyForm(instance=prop, prefix="prop")

    images = prop.images.all()

    return render(
        request,
        "properties/property_edit.html",
        {
            "loc_form": loc_form,
            "prop_form": prop_form,
            "prop": prop,
            "images": images,
        },
    )
    
@login_required
def property_delete(request, pk: int):
    if not require_host(request):
        return redirect("accounts:toggle_mode")

    agent, _ = AgentProfile.objects.get_or_create(user=request.user)

    prop = Property.objects.select_related("agent").filter(pk=pk).first()
    if not prop:
        raise Http404("Property not found")

    if prop.agent_id != agent.id:
        raise Http404("You do not have permission to delete this property")

    if request.method == "POST":
        prop.delete()
        return redirect("properties:mine")

    return render(
        request,
        "properties/property_delete.html",
        {
            "prop": prop,
        },
    )

@login_required
def contact_advisor(request, pk):
    property_obj = get_object_or_404(Property.objects.select_related("agent__user"), pk=pk)

    advisor = property_obj.agent.user

    conversation, created = Conversation.objects.get_or_create(
        property=property_obj,
        buyer=request.user,
        advisor=advisor,
    )

    if created:
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=f"Hola, estoy interesado en la propiedad #{property_obj.pk}."
        )

    return redirect("interactions:chat_room", conversation_id=conversation.id)


@login_required
def create_checkout_session(request, pk: int):
    if request.method != "POST":
        raise Http404("Method not allowed")

    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLISHABLE_KEY:
        messages.error(request, "Stripe no esta configurado todavia.")
        return redirect("properties:detail", pk=pk)

    property_obj = get_object_or_404(
        Property.objects.select_related("location"),
        pk=pk,
        is_active=True,
    )

    stripe.api_key = settings.STRIPE_SECRET_KEY
    amount_in_cents = int((property_obj.price * Decimal("100")).quantize(Decimal("1")))

    checkout_session = stripe.checkout.Session.create(
        mode="payment",
        success_url=request.build_absolute_uri(
            f"/properties/{property_obj.pk}/payment/success/"
        ) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(
            f"/properties/{property_obj.pk}/payment/cancel/"
        ),
        customer_email=request.user.email or None,
        metadata={
            "property_id": str(property_obj.pk),
            "user_id": str(request.user.pk),
        },
        line_items=[
            {
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY,
                    "unit_amount": amount_in_cents,
                    "product_data": {
                        "name": property_obj.title,
                        "description": f"{property_obj.get_operation_display()} en {property_obj.location.city}",
                    },
                },
                "quantity": 1,
            }
        ],
    )

    PropertyPayment.objects.update_or_create(
        stripe_session_id=checkout_session.id,
        defaults={
            "property": property_obj,
            "user": request.user,
            "amount": property_obj.price,
            "currency": settings.STRIPE_CURRENCY,
            "status": PropertyPayment.STATUS_PENDING,
        },
    )

    return redirect(checkout_session.url, permanent=False)


@login_required
def payment_success(request, pk: int):
    property_obj = get_object_or_404(Property, pk=pk)
    session_id = request.GET.get("session_id", "").strip()
    payment = None

    if session_id and settings.STRIPE_SECRET_KEY:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        payment = PropertyPayment.objects.filter(
            stripe_session_id=session_id,
            property=property_obj,
            user=request.user,
        ).first()

        if payment:
            sync_payment_from_checkout_session(payment, checkout_session)

    return render(
        request,
        "properties/payment_success.html",
        {
            "prop": property_obj,
            "payment": payment,
        },
    )


@login_required
def payment_cancel(request, pk: int):
    property_obj = get_object_or_404(Property, pk=pk)
    pending_payment = (
        PropertyPayment.objects.filter(
            property=property_obj,
            user=request.user,
            status=PropertyPayment.STATUS_PENDING,
        )
        .order_by("-created_at")
        .first()
    )
    if pending_payment:
        pending_payment.status = PropertyPayment.STATUS_CANCELED
        pending_payment.save(update_fields=["status"])

    return render(
        request,
        "properties/payment_cancel.html",
        {
            "prop": property_obj,
        },
    )


@csrf_exempt
def stripe_webhook(request):
    if request.method != "POST":
        raise Http404("Method not allowed")

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    if not settings.STRIPE_WEBHOOK_SECRET:
        return JsonResponse(
            {"detail": "Stripe webhook secret is not configured."},
            status=503,
        )

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        payment = PropertyPayment.objects.filter(
            stripe_session_id=session.get("id", "")
        ).first()
        if payment:
            sync_payment_from_checkout_session(payment, session)

    if event["type"] == "checkout.session.expired":
        session = event["data"]["object"]
        payment = PropertyPayment.objects.filter(
            stripe_session_id=session.get("id", "")
        ).first()
        if payment:
            payment.status = PropertyPayment.STATUS_FAILED
            payment.save(update_fields=["status"])

    return HttpResponse(status=200)
