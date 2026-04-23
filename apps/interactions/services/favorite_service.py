from apps.interactions.repositories.favorite_repository import FavoriteRepository


from django.core.exceptions import ValidationError

class FavoriteService:
    def __init__(self, repository=None):
        self.repository = repository or FavoriteRepository()

    def is_favorite(self, user, property_obj):
        if not user.is_authenticated:
            return False
        return self.repository.is_favorite(user, property_obj)

    def add_to_favorites(self, user, property_obj):
        if not user.is_authenticated:
            return None, False
            
        if getattr(property_obj, 'agent_id', None) is not None:
            if hasattr(user, 'agent_profile') and property_obj.agent == user.agent_profile:
                raise ValidationError("No puedes agregar tu propia propiedad a favoritos.")
                
        if not getattr(property_obj, 'is_active', True):
            raise ValidationError("No puedes agregar a favoritos una propiedad inactiva.")
            
        return self.repository.get_or_create(user, property_obj)

    def remove_from_favorites(self, user, property_obj):
        if not user.is_authenticated:
            return False
        return self.repository.remove(user, property_obj)