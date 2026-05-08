from urllib.parse import urlparse
from app.core.config import settings


ALLOWED_SCHEMES = {"http", "https"}


def is_url_allowed(url: str) -> tuple[bool, str | None]:
    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, f"URL scheme not allowed: {parsed.scheme}"

    hostname = parsed.hostname

    if not hostname:
        return False, "URL hostname is missing"

    hostname = hostname.lower()

    if hostname in settings.blocked_domains:
        return False, f"Domain is blocked: {hostname}"

    return True, None


def deduplicate_urls(urls: list[str]) -> list[str]:
    seen = set()
    deduplicated = []

    for url in urls:
        normalized = url.strip()

        if normalized not in seen:
            seen.add(normalized)
            deduplicated.append(normalized)

    return deduplicated