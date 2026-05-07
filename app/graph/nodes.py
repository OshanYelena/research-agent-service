from app.core.logging import logger
from app.crawler.http_client import fetch_html
from app.crawler.extractor import extract_text_from_html
from app.graph.state import ResearchState


def create_search_plan(state: ResearchState) -> dict:
    query = state["query"]
    urls = state["urls"]

    logger.info(
        "creating_search_plan",
        query=query,
        url_count=len(urls),
    )

    return {
        "search_plan": f"Crawl {len(urls)} user-provided URLs and summarize information related to: {query}"
    }


def crawl_urls(state: ResearchState) -> dict:
    sources = []

    for url in state["urls"]:
        status_code, html, error = fetch_html(url)

        if error:
            sources.append(
                {
                    "url": url,
                    "status_code": status_code,
                    "title": None,
                    "content": None,
                    "error": error,
                }
            )
            continue

        title, content = extract_text_from_html(html)

        sources.append(
            {
                "url": url,
                "status_code": status_code,
                "title": title,
                "content": content,
                "error": None,
            }
        )

    return {"sources": sources}


def summarize_sources(state: ResearchState) -> dict:
    valid_sources = [
        source for source in state["sources"]
        if source.get("content")
    ]

    if not valid_sources:
        return {
            "summary": "No readable source content could be extracted from the provided URLs."
        }

    source_summaries = []

    for source in valid_sources:
        preview = source["content"][:500]
        source_summaries.append(
            f"Source: {source.get('title') or source['url']} — {preview}"
        )

    summary = " ".join(source_summaries)

    logger.info(
        "summarized_sources",
        valid_source_count=len(valid_sources),
    )

    return {"summary": summary}