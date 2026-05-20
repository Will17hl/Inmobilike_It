import logging

from apps.properties.models import PropertyImage
from apps.properties.repositories.property_repository import PropertyRepository


logger = logging.getLogger(__name__)


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

        PropertyService.add_property_images(prop, files)

        return prop

    @staticmethod
    def add_property_images(property_obj, files=None):
        saved_images = []
        if not files:
            return saved_images

        has_cover = property_obj.images.filter(is_cover=True).exists()
        for image_file in files:
            try:
                saved_images.append(
                    PropertyImage.objects.create(
                        property=property_obj,
                        image=image_file,
                        is_cover=(not has_cover and not saved_images),
                    )
                )
            except Exception:
                logger.exception("Could not save uploaded image for property %s", property_obj.pk)

        return saved_images
