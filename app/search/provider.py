from abc import ABC, abstractmethod

from app.search.models import SearchResult


class SearchProvider(ABC):
    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        raise NotImplementedError