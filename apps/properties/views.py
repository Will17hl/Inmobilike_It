from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from apps.interactions.models import Conversation, Message
from apps.accounts.models import AgentProfile
from apps.interactions.models import Favorite
from .forms import PropertyForm, LocationForm
from .services.property_service import PropertyService
from .models import Property, PropertyImage
from decimal import Decimal, InvalidOperation

def require_host(request):
    return request.session.get("mode", "guest") == "host"


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