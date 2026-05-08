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