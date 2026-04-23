from .base import PropertySearchEngine

class ElasticPropertySearch(PropertySearchEngine):
    def search(self, filters: dict) -> list:
        # Aquí iría la integración real con Elasticsearch
        # Ejemplo: return es_client.search(index="properties", body=build_es_query(filters))
        return []
