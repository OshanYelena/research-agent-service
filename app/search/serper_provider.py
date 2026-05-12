import httpx

from app.core.config import settings
from app.core.logging import logger
from app.search.models import SearchResult
from app.search.provider import SearchProvider


class SerperSearchProvider(SearchProvider):
    BASE_URL = "https://google.serper.dev/search"

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        if not settings.SERPER_API_KEY:
            logger.warning("serper_api_key_missing")
            return []

        headers = {
            "X-API-KEY": settings.SERPER_API_KEY,
            "Content-Type": "application/json",
        }

        payload = {
            "q": query,
            "num": max_results,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.SEARCH_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                )

            response.raise_for_status()

            data = response.json()

            organic_results = data.get("organic", [])

            results: list[SearchResult] = []

            for index, item in enumerate(organic_results[:max_results], start=1):
                link = item.get("link")

                if not link:
                    continue

                results.append(
                    SearchResult(
                        title=item.get("title"),
                        url=link,
                        snippet=item.get("snippet"),
                        source="serper",
                        rank=index,
                    )
                )

            logger.info(
                "serper_search_completed",
                query=query,
                result_count=len(results),
            )

            return results

        except httpx.HTTPError as exc:
            logger.warning(
                "serper_search_failed",
                query=query,
                error_type=type(exc).__name__,
                error=str(exc) or repr(exc),
            )
            return []
