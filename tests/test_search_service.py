from app.search.models import SearchResult
from app.search.provider import SearchProvider
from app.search.service import SearchService
import pytest

class MockSearchProvider(SearchProvider):
    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        return [
            SearchResult(
                title=f"{query} Result",
                url="https://example.com/article",
                snippet="AI agent framework content",
                source="mock",
                rank=1,
            ),
            SearchResult(
                title="Duplicate Result",
                url="https://example.com/article",
                snippet="duplicate",
                source="mock",
                rank=2,
            ),
        ]

@pytest.mark.anyio
async def test_search_service_discovers_deduplicated_urls():
    service = SearchService(providers=[MockSearchProvider()])

    urls = await service.discover_urls(
        query="ai agent framework",
        max_results=5,
    )

    assert urls == ["https://example.com/article"]

@pytest.mark.anyio
async def test_search_service_discovers_ranked_results():
    service = SearchService(providers=[MockSearchProvider()])

    results = await service.discover_results(
        query="ai agent framework",
        max_results=5,
    )

    assert len(results) == 1
    assert results[0].url.host == "example.com"

import pytest

from app.search.models import SearchResult
from app.search.provider import SearchProvider
from app.search.service import SearchService


class QueryTrackingProvider(SearchProvider):
    def __init__(self):
        self.seen_queries: list[str] = []

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        self.seen_queries.append(query)

        return [
            SearchResult(
                title=f"{query} Result",
                url=f"https://example.com/{len(self.seen_queries)}",
                snippet="AI agent framework content",
                source="mock",
                rank=1,
            )
        ]


@pytest.mark.anyio
async def test_search_service_uses_planner_queries_when_provided():
    provider = QueryTrackingProvider()
    service = SearchService(providers=[provider])

    await service.discover_urls(
        query="original query",
        max_results=5,
        search_queries=[
            "planner query one",
            "planner query two",
        ],
    )

    assert provider.seen_queries == [
        "planner query one",
        "planner query two",
    ]