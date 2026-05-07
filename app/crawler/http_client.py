import httpx

from app.core.config import settings
from app.core.logging import logger


def fetch_html(url: str) -> tuple[int | None, str | None, str | None]:
    headers = {
        "User-Agent": settings.CRAWLER_USER_AGENT
    }

    try:
        logger.info("fetching_url", url=url)

        with httpx.Client(
            headers=headers,
            timeout=settings.CRAWLER_TIMEOUT_SECONDS,
            follow_redirects=True,
        ) as client:
            response = client.get(url)

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