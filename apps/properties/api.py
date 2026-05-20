from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .repositories.property_repository import PropertyRepository


def _serialize_property(prop):
    cover = None
    cover_obj = prop.images.filter(is_cover=True).first() or prop.images.first()
    if cover_obj:
        cover = cover_obj.image_url or (getattr(cover_obj.image, 'url', None) if hasattr(cover_obj, 'image') else None)

    return {
        "id": prop.id,
        "title": prop.title,
        "description": (prop.description[:240] + "...") if prop.description and len(prop.description) > 240 else prop.description,
        "price": str(prop.price),
        "operation": prop.operation,
        "city": prop.location.city if prop.location else None,
        "neighborhood": prop.location.neighborhood if prop.location else None,
        "cover_url": cover,
    }


@require_GET
def properties_list_api(request):
    # Parámetros de paginación
    page = int(request.GET.get("page", "1") or 1)
    page_size = int(request.GET.get("page_size", "10") or 10)

    filters = {
        "city": request.GET.get("city"),
        "neighborhood": request.GET.get("neighborhood"),
        "operation": request.GET.get("operation"),
        "min_price": request.GET.get("min_price"),
        "max_price": request.GET.get("max_price"),
    }

    qs = PropertyRepository.get_active_properties(filters=filters)

    paginator = Paginator(qs, page_size)

    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        return JsonResponse({"results": [], "page": page, "page_size": page_size, "total_pages": paginator.num_pages, "total": paginator.count})

    results = [_serialize_property(p) for p in page_obj.object_list]

    return JsonResponse({
        "results": results,
        "page": page,
        "page_size": page_size,
        "total_pages": paginator.num_pages,
        "total": paginator.count,
    })
