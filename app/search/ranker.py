from app.search.models import SearchResult


def _tokenize(text: str) -> set[str]:
    return {
        token.lower().strip(".,!?;:()[]{}\"'")
        for token in text.split()
        if token.strip()
    }


def score_search_result(query: str, result: SearchResult) -> float:
    query_tokens = _tokenize(query)

    title_tokens = _tokenize(result.title or "")
    snippet_tokens = _tokenize(result.snippet or "")

    title_overlap = len(query_tokens & title_tokens)
    snippet_overlap = len(query_tokens & snippet_tokens)

    provider_rank_score = 0.0

    if result.rank:
        provider_rank_score = max(0.0, 1.0 - ((result.rank - 1) * 0.1))

    score = (
        title_overlap * 2.0
        + snippet_overlap * 1.0
        + provider_rank_score
    )

    return score


def rank_search_results(
    query: str,
    results: list[SearchResult],
) -> list[SearchResult]:
    return sorted(
        results,
        key=lambda result: score_search_result(query, result),
        reverse=True,
    )