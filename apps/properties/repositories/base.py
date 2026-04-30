from abc import ABC, abstractmethod

class PropertySearchEngine(ABC):
    @abstractmethod
    def search(self, filters: dict) -> list:
        pass
