from apps.properties.models import PropertyImage
from apps.properties.repositories.property_repository import PropertyRepository


class PropertyService:
    @staticmethod
    def list_active_properties(filters=None):
        return PropertyRepository.get_active_properties(filters=filters)

    @staticmethod
    def get_property_detail(property_id):
        return PropertyRepository.get_property_by_id(property_id)

    @staticmethod
    def get_agent_properties(agent):
        return PropertyRepository.get_properties_by_agent(agent)

    @staticmethod
    def get_cover_image(property_obj):
        return property_obj.images.filter(is_cover=True).first() or property_obj.images.first()

    @staticmethod
    def get_property_images(property_obj):
        return property_obj.images.order_by("-is_cover", "id")

    @staticmethod
    def create_property(agent, location_form, property_form, files=None):
        location = location_form.save()

        prop = property_form.save(commit=False)
        prop.location = location
        prop.agent = agent
        prop.save()

        if files:
            for i, f in enumerate(files):
                PropertyImage.objects.create(
                    property=prop,
                    image=f,
                    is_cover=(i == 0),
                )

        return prop