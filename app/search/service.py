import asyncio

from app.core.config import settings
from app.core.logging import logger
# from app.search.brave_provider import BraveSearchProvider
from app.search.models import SearchResult
from app.search.normalizer import extract_urls_from_results, normalize_search_results
from app.search.query_expander import expand_query
from app.search.ranker import rank_search_results
from app.search.provider import SearchProvider
from app.search.serper_provider import SerperSearchProvider


class SearchService:
    def __init__(self, providers: list[SearchProvider] | None = None):
        self.providers = providers or [SerperSearchProvider()]

    async def discover_results(
            self,
            query: str,
            max_results: int | None = None,
            search_queries: list[str] | None = None,
    ) -> list[SearchResult]:
        max_results = max_results or settings.SEARCH_MAX_RESULTS
        expanded_queries = search_queries or expand_query(query)

        logger.info(
            "discovering_search_results",
            query=query,
            expanded_query_count=len(expanded_queries),
            provider_count=len(self.providers),
        )

        tasks = []

        for expanded_query in expanded_queries:
            for provider in self.providers:
                tasks.append(
                    provider.search(
                        query=expanded_query,
                        max_results=max_results,
                    )
                )

        provider_result_groups = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        merged_results: list[SearchResult] = []

        for group in provider_result_groups:
            if isinstance(group, Exception):
                logger.warning(
                    "search_provider_task_failed",
                    error=str(group),
                )
                continue

            merged_results.extend(group)

        normalized_results = normalize_search_results(merged_results)
        ranked_results = rank_search_results(query, normalized_results)

        logger.info(
            "search_discovery_completed",
            merged_count=len(merged_results),
            normalized_count=len(normalized_results),
            ranked_count=len(ranked_results),
        )

        return ranked_results[:max_results]

    async def discover_urls(
            self,
            query: str,
            max_results: int | None = None,
            search_queries: list[str] | None = None,
    ) -> list[str]:
        results = await self.discover_results(
            query=query,
            max_results=max_results,
            search_queries=search_queries,
        )

        return extract_urls_from_results(results)