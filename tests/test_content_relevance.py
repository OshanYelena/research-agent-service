from app.summarization.relevance import (
    rank_sources_by_relevance,
    score_content_relevance,
)


def test_score_content_relevance_prefers_matching_content():
    query = "ai agent framework"

    strong_source = {
        "title": "AI Agent Framework Guide",
        "content": "This article explains AI agent framework design.",
        "word_count": 200,
        "extraction_quality": "medium",
        "extraction_quality_score": 0.7,
    }

    weak_source = {
        "title": "Random News",
        "content": "This article discusses cooking and travel.",
        "word_count": 200,
        "extraction_quality": "medium",
        "extraction_quality_score": 0.7,
    }

    assert score_content_relevance(query, strong_source) > score_content_relevance(query, weak_source)


def test_rank_sources_by_relevance_orders_best_first():
    query = "ai agent framework"

    sources = [
        {
            "url": "https://example.com/weak",
            "title": "Random News",
            "content": "This article discusses cooking and travel.",
            "word_count": 200,
            "extraction_quality": "medium",
            "extraction_quality_score": 0.7,
        },
        {
            "url": "https://example.com/strong",
            "title": "AI Agent Framework Guide",
            "content": "This article explains AI agent framework design.",
            "word_count": 200,
            "extraction_quality": "medium",
            "extraction_quality_score": 0.7,
        },
    ]

    ranked = rank_sources_by_relevance(query, sources)

    assert ranked[0]["url"] == "https://example.com/strong"
    assert "content_relevance_score" in ranked[0]