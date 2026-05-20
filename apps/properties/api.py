from django.core.paginator import Paginator, EmptyPage
from django.db import DatabaseError
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .repositories.property_repository import PropertyRepository


MAX_PAGE_SIZE = 50


def _positive_int(value, default):
    try:
        number = int(value or default)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


def _serialize_property(prop):
    return {
        "id": prop.id,
        "title": prop.title,
        "description": (prop.description[:240] + "...") if prop.description and len(prop.description) > 240 else prop.description,
        "price": str(prop.price),
        "operation": prop.operation,
        "city": prop.location.city if prop.location else None,
        "neighborhood": prop.location.neighborhood if prop.location else None,
        "cover_url": prop.cover_display_url,
    }


@require_GET
def properties_list_api(request):
    # Parámetros de paginación
    page = _positive_int(request.GET.get("page"), 1)
    page_size = min(_positive_int(request.GET.get("page_size"), 10), MAX_PAGE_SIZE)

    filters = {
        "city": request.GET.get("city"),
        "neighborhood": request.GET.get("neighborhood"),
        "operation": request.GET.get("operation"),
        "min_price": request.GET.get("min_price"),
        "max_price": request.GET.get("max_price"),
    }

    try:
        qs = PropertyRepository.get_active_properties(filters=filters)

        paginator = Paginator(qs, page_size)

        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            return JsonResponse({"results": [], "page": page, "page_size": page_size, "total_pages": paginator.num_pages, "total": paginator.count})

        results = [_serialize_property(p) for p in page_obj.object_list]
    except DatabaseError:
        return JsonResponse({"error": "Database unavailable"}, status=503)

    return JsonResponse({
        "results": results,
        "page": page,
        "page_size": page_size,
        "total_pages": paginator.num_pages,
        "total": paginator.count,
    })
