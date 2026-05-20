from abc import ABC, abstractmethod
from io import BytesIO

from .data import build_properties_rows


class PropertyReportExporter(ABC):
    """Interfaz DIP: exportación de listados de propiedades en distintos formatos."""

    @abstractmethod
    def export(self, filters=None) -> BytesIO:
        pass

    def build_rows(self, filters=None):
        return build_properties_rows(filters=filters)
