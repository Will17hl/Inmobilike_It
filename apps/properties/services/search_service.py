from apps.properties.repositories.base import PropertySearchEngine
from apps.properties.repositories.orm_search import ORMPropertySearch

class AdvancedSearchService:
    def __init__(self, search_engine: PropertySearchEngine = None):
        self.search_engine = search_engine or ORMPropertySearch()

    def search(self, query_params: dict) -> list:
        return self.search_engine.search(query_params)
