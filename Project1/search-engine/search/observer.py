from abc import ABC, abstractmethod

class SearchObserver(ABC):
    @abstractmethod
    def on_search(self, query: str, results: list[dict]):
        pass