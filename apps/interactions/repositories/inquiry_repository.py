from apps.interactions.models import Inquiry


class InquiryRepository:
    @staticmethod
    def create(**kwargs):
        return Inquiry.objects.create(**kwargs)