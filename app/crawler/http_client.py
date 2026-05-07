import httpx

from app.core.config import settings
from app.core.logging import logger


def _build_headers() -> dict[str, str]:
    return {
        "User-Agent": settings.CRAWLER_USER_AGENT,
    }


async def fetch_html_async(
    client: httpx.AsyncClient,
    url: str,
) -> tuple[int | None, str | None, str | None]:
    try:
        logger.info("fetching_url", url=url)

        response = await client.get(url)

        content_type = response.headers.get("content-type", "")

        if "text/html" not in content_type:
            return response.status_code, None, f"Unsupported content type: {content_type}"

        response.raise_for_status()

        html = response.text[: settings.CRAWLER_MAX_CONTENT_CHARS]

        return response.status_code, html, None

    except httpx.TimeoutException:
        logger.warning("fetch_timeout", url=url)
        return None, None, "Request timed out"

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "fetch_http_error",
            url=url,
            status_code=exc.response.status_code,
        )
        return exc.response.status_code, None, str(exc)

    except httpx.RequestError as exc:
        logger.warning("fetch_request_error", url=url, error=str(exc))
        return None, None, str(exc)


async def create_async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers=_build_headers(),
        timeout=settings.CRAWLER_TIMEOUT_SECONDS,
        follow_redirects=True,
    )