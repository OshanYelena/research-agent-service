from bs4 import BeautifulSoup
from readability import Document

from app.core.config import settings


def _clean_text(text: str) -> str:
    return " ".join(text.split())


def assess_extraction_quality(text: str | None) -> tuple[str, float]:
    if not text:
        return "failed", 0.0

    length = len(text)

    if length >= 1000:
        return "high", 1.0

    if length >= 400:
        return "medium", 0.7

    if length >= 100:
        return "low", 0.4

    return "very_low", 0.2



def _extract_title_from_soup(soup: BeautifulSoup) -> str | None:
    if soup.title and soup.title.string:
        return _clean_text(soup.title.string)

    h1 = soup.find("h1")
    if h1:
        return _clean_text(h1.get_text(" ", strip=True))

    return None


def _fallback_extract_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()

    article = soup.find("article")
    main = soup.find("main")

    target = article or main or soup.body or soup

    return _clean_text(target.get_text(" ", strip=True))


def extract_text_from_html(
    html: str,
) -> tuple[str | None, str | None, str, float]:
    soup = BeautifulSoup(html, "lxml")
    fallback_title = _extract_title_from_soup(soup)

    try:
        document = Document(html)

        title = document.short_title() or fallback_title
        summary_html = document.summary()

        summary_soup = BeautifulSoup(summary_html, "lxml")

        for tag in summary_soup(["script", "style", "noscript"]):
            tag.decompose()

        text = _clean_text(summary_soup.get_text(" ", strip=True))

        if text:
            quality, score = assess_extraction_quality(text)
            return title, text, quality, score

    except Exception:
        pass

    fallback_text = _fallback_extract_text(soup)
    quality, score = assess_extraction_quality(fallback_text)

    return fallback_title, fallback_text, quality, score