from app.search.models import SearchResult
from app.search.normalizer import normalize_search_results, extract_urls_from_results


def test_normalize_search_results_removes_duplicates():
    results = [
        SearchResult(
            title="One",
            url="https://example.com",
            snippet="A",
            source="test",
            rank=1,
        ),
        SearchResult(
            title="Duplicate",
            url="https://example.com",
            snippet="B",
            source="test",
            rank=2,
        ),
    ]

    normalized = normalize_search_results(results)

    assert len(normalized) == 1


def test_normalize_search_results_blocks_unsafe_urls():
    results = [
        SearchResult(
            title="Unsafe",
            url="http://localhost:8000",
            snippet="local",
            source="test",
            rank=1,
        ),
        SearchResult(
            title="Safe",
            url="https://example.com",
            snippet="safe",
            source="test",
            rank=2,
        ),
    ]

    normalized = normalize_search_results(results)

    assert len(normalized) == 1
    assert normalized[0].title == "Safe"


def test_extract_urls_from_results():
    results = [
        SearchResult(
            title="One",
            url="https://example.com",
            snippet="A",
            source="test",
            rank=1,
        )
    ]

    urls = extract_urls_from_results(results)

    assert urls == ["https://example.com/"]