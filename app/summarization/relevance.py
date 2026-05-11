from app.search.ranker import _tokenize


def score_content_relevance(query: str, source: dict) -> float:
    content = source.get("content") or ""
    title = source.get("title") or ""

    query_tokens = _tokenize(query)
    title_tokens = _tokenize(title)
    content_tokens = _tokenize(content)

    if not query_tokens or not content_tokens:
        return 0.0

    title_overlap = len(query_tokens & title_tokens)
    content_overlap = len(query_tokens & content_tokens)

    extraction_quality_score = source.get("extraction_quality_score") or 0.0
    word_count = source.get("word_count") or 0

    richness_score = min(word_count / 500, 1.0)

    raw_score = (
        title_overlap * 2.0
        + content_overlap * 1.0
        + extraction_quality_score * 2.0
        + richness_score
    )

    quality_cap = {
        "high": 10.0,
        "medium": 7.0,
        "low": 4.0,
        "very_low": 2.0,
        "failed": 0.0,
    }

    extraction_quality = source.get("extraction_quality") or "failed"
    capped_score = min(
        raw_score,
        quality_cap.get(extraction_quality, 0.0),
    )

    return round(capped_score, 3)


def rank_sources_by_relevance(
    query: str,
    sources: list[dict],
) -> list[dict]:
    scored_sources = []

    for source in sources:
        relevance_score = score_content_relevance(query, source)

        enriched_source = {
            **source,
            "content_relevance_score": relevance_score,
        }

        scored_sources.append(enriched_source)

    return sorted(
        scored_sources,
        key=lambda item: item.get("content_relevance_score", 0.0),
        reverse=True,
    )