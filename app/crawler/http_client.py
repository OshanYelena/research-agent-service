import httpx

from app.core.logging import logger


DEFAULT_HEADERS = {
    "User-Agent": "ResearchAgentService/0.1 (+https://example.com/bot)"
}


def fetch_html(url: str, timeout: float = 10.0) -> tuple[int | None, str | None, str | None]:
    try:
        logger.info("fetching_url", url=url)

        with httpx.Client(
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            response = client.get(url)

        content_type = response.headers.get("content-type", "")

        if "text/html" not in content_type:
            return response.status_code, None, f"Unsupported content type: {content_type}"

        response.raise_for_status()

        return response.status_code, response.text, None

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