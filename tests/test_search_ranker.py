from app.search.models import SearchResult
from app.search.ranker import rank_search_results, score_search_result


def test_score_search_result_prefers_title_overlap():
    query = "ai agent framework"

    strong_result = SearchResult(
        title="AI Agent Framework Guide",
        url="https://example.com/strong",
        snippet="A guide about software systems.",
        source="test",
        rank=2,
    )

    weak_result = SearchResult(
        title="Random Article",
        url="https://example.com/weak",
        snippet="No matching terms here.",
        source="test",
        rank=1,
    )

    assert score_search_result(query, strong_result) > score_search_result(query, weak_result)


def test_rank_search_results_orders_best_first():
    query = "ai agent framework"

    results = [
        SearchResult(
            title="Random Article",
            url="https://example.com/weak",
            snippet="No matching terms here.",
            source="test",
            rank=1,
        ),
        SearchResult(
            title="AI Agent Framework Guide",
            url="https://example.com/strong",
            snippet="A guide about software systems.",
            source="test",
            rank=2,
        ),
    ]

    ranked = rank_search_results(query, results)

    assert ranked[0].title == "AI Agent Framework Guide"