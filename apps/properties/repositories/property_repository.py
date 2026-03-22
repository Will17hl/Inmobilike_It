from decimal import Decimal, InvalidOperation
from apps.properties.models import Property
from apps.properties.utils import normalize_decimal_input


class PropertyRepository:
    @staticmethod
    def get_active_properties(filters=None):
        qs = (
            Property.objects
            .filter(is_active=True)
            .select_related("location", "agent")
            .prefetch_related("images")
            .order_by("-created_at")
        )

        if not filters:
            return qs

        city = (filters.get("city") or "").strip()
        neighborhood = (filters.get("neighborhood") or "").strip()
        operation = (filters.get("operation") or "").strip()
        min_price = normalize_decimal_input(filters.get("min_price"))
        max_price = normalize_decimal_input(filters.get("max_price"))

        if city:
            qs = qs.filter(location__city__icontains=city)

        if neighborhood:
            qs = qs.filter(location__neighborhood__icontains=neighborhood)

        if operation in {"rent", "sale"}:
            qs = qs.filter(operation=operation)

        if min_price:
            try:
                qs = qs.filter(price__gte=Decimal(min_price))
            except (InvalidOperation, ValueError):
                pass

        if max_price:
            try:
                qs = qs.filter(price__lte=Decimal(max_price))
            except (InvalidOperation, ValueError):
                pass

        return qs

    @staticmethod
    def get_property_by_id(property_id):
        return (
            Property.objects
            .select_related("location", "agent")
            .prefetch_related("images")
            .filter(pk=property_id, is_active=True)
            .first()
        )

    @staticmethod
    def get_properties_by_agent(agent):
        return (
            Property.objects
            .filter(agent=agent)
            .select_related("location", "agent")
            .prefetch_related("images")
            .order_by("-created_at")
        )
