from django.db import IntegrityError

from apps.interactions.models import Favorite


class FavoriteRepository:
    @staticmethod
    def is_favorite(user, property_obj):
        return Favorite.objects.filter(user=user, property=property_obj).exists()

    @staticmethod
    def get_or_create(user, property_obj):
        try:
            return Favorite.objects.get_or_create(user=user, property=property_obj)
        except IntegrityError:
            favorite = Favorite.objects.filter(user=user, property=property_obj).first()
            return favorite, False

    @staticmethod
    def remove(user, property_obj):
        deleted_count, _ = Favorite.objects.filter(
            user=user,
            property=property_obj,
        ).delete()
        return deleted_count > 0