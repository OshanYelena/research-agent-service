from bs4 import BeautifulSoup
from readability import Document


def extract_text_from_html(html: str) -> tuple[str | None, str | None]:
    document = Document(html)

    title = document.short_title()
    summary_html = document.summary()

    soup = BeautifulSoup(summary_html, "lxml")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    cleaned_text = " ".join(text.split())

    return title, cleaned_text