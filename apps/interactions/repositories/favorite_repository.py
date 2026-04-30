from django.db import IntegrityError

from apps.interactions.models import Favorite


class FavoriteRepository:
    def is_favorite(self, user, property_obj):
        return Favorite.objects.filter(user=user, property=property_obj).exists()

    def get_or_create(self, user, property_obj):
        return Favorite.objects.get_or_create(user=user, property=property_obj)

    def remove(self, user, property_obj):
        deleted_count, _ = Favorite.objects.filter(
            user=user,
            property=property_obj,
        ).delete()
        return deleted_count > 0