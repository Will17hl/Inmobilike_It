from apps.interactions.repositories.inquiry_repository import InquiryRepository


class InquiryService:
    @staticmethod
    def create_inquiry(property_obj, user=None, name="", email="", message=""):
        inquiry_data = {
            "property": property_obj,
            "name": name,
            "email": email,
            "message": message,
        }

        if user and user.is_authenticated:
            inquiry_data["user"] = user

        return InquiryRepository.create(**inquiry_data)