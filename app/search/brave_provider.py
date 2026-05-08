import httpx

from app.core.config import settings
from app.core.logging import logger
from app.search.models import SearchResult
from app.search.provider import SearchProvider


class BraveSearchProvider(SearchProvider):
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        if not settings.BRAVE_SEARCH_API_KEY:
            logger.warning("brave_search_api_key_missing")
            return []

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": settings.BRAVE_SEARCH_API_KEY,
        }

        params = {
            "q": query,
            "count": max_results,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.BASE_URL,
                    headers=headers,
                    params=params,
                )

            response.raise_for_status()
            payload = response.json()

            web_results = payload.get("web", {}).get("results", [])

            results: list[SearchResult] = []

            for index, item in enumerate(web_results, start=1):
                url = item.get("url")

                if not url:
                    continue

                results.append(
                    SearchResult(
                        title=item.get("title"),
                        url=url,
                        snippet=item.get("description"),
                        source="brave",
                        rank=index,
                    )
                )

            logger.info(
                "brave_search_completed",
                query=query,
                result_count=len(results),
            )

            return results

        except httpx.HTTPError as exc:
            logger.warning(
                "brave_search_failed",
                query=query,
                error=str(exc),
            )
            return []