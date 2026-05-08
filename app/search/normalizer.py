from app.crawler.url_safety import deduplicate_urls, is_url_allowed
from app.search.models import SearchResult


def normalize_search_results(
    results: list[SearchResult],
) -> list[SearchResult]:
    normalized_results: list[SearchResult] = []
    seen_urls = set()

    for result in results:
        url = str(result.url).strip()

        if url in seen_urls:
            continue

        allowed, _ = is_url_allowed(url)

        if not allowed:
            continue

        seen_urls.add(url)

        normalized_results.append(result)

    return normalized_results


def extract_urls_from_results(
    results: list[SearchResult],
) -> list[str]:
    urls = [str(result.url) for result in results]
    return deduplicate_urls(urls)