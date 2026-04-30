from apps.properties.models import Property

class ComparisonService:
    def compare_properties(self, property_ids):
        if not property_ids:
            return []
            
        properties = Property.objects.select_related("location").prefetch_related("images").filter(id__in=property_ids)
        
        comparison_data = []
        for prop in properties:
            cover = prop.images.filter(is_cover=True).first() or prop.images.first()
            cover_url = cover.image.url if cover and cover.image else (cover.image_url if cover else None)
            
            comparison_data.append({
                "id": prop.id,
                "title": prop.title,
                "operation": prop.get_operation_display(),
                "price": prop.price,
                "bedrooms": prop.bedrooms,
                "bathrooms": prop.bathrooms,
                "area_m2": prop.area_m2,
                "location": str(prop.location),
                "cover_url": cover_url,
                "price_per_m2": round(prop.price / prop.area_m2, 2) if prop.area_m2 and prop.area_m2 > 0 else None
            })
            
        return comparison_data
