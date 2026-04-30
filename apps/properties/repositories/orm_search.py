from django.db.models import Q
from apps.properties.models import Property
from .base import PropertySearchEngine

class ORMPropertySearch(PropertySearchEngine):
    def search(self, filters: dict) -> list:
        queryset = Property.objects.select_related("location").filter(is_active=True)

        operation = filters.get("operation")
        if operation:
            queryset = queryset.filter(operation=operation)

        min_price = filters.get("min_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = filters.get("max_price")
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        bedrooms = filters.get("bedrooms")
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=bedrooms)
            
        bathrooms = filters.get("bathrooms")
        if bathrooms:
            queryset = queryset.filter(bathrooms__gte=bathrooms)

        location = filters.get("location")
        if location:
            queryset = queryset.filter(
                Q(location__city__icontains=location) | 
                Q(location__neighborhood__icontains=location) |
                Q(title__icontains=location)
            )

        return list(queryset.distinct())
