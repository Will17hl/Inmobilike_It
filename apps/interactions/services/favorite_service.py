from apps.interactions.repositories.favorite_repository import FavoriteRepository


class FavoriteService:
    @staticmethod
    def is_favorite(user, property_obj):
        if not user.is_authenticated:
            return False
        return FavoriteRepository.is_favorite(user, property_obj)

    @staticmethod
    def add_to_favorites(user, property_obj):
        if not user.is_authenticated:
            return None, False
        return FavoriteRepository.get_or_create(user, property_obj)

    @staticmethod
    def remove_from_favorites(user, property_obj):
        if not user.is_authenticated:
            return False
        return FavoriteRepository.remove(user, property_obj)