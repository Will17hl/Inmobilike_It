from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from apps.properties.services.property_service import PropertyService
from .forms import InquiryForm
from .services.favorite_service import FavoriteService
from .services.inquiry_service import InquiryService


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