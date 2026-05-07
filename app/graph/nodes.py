import asyncio

from app.core.config import settings
from app.core.logging import logger
from app.crawler.http_client import create_async_client, fetch_html_async
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
        "search_plan": f"Crawl {len(urls)} user-provided URLs concurrently and summarize information related to: {query}"
    }


async def _crawl_single_url(client, url: str, semaphore: asyncio.Semaphore) -> dict:

    async with semaphore:
        status_code, html, error = await fetch_html_async(client, url)
        if error:
            return {
                "url": url,
                "status_code": status_code,
                "title": None,
                "content": None,
                "error": error,
            }

        title, content = extract_text_from_html(html)

        return {
            "url": url,
            "status_code": status_code,
            "title": title,
            "content": content,
            "error": None,
        }

async def crawl_urls(state: ResearchState) -> dict:
    urls = state["urls"]

    if not urls:
        return {"sources": []}

    logger.info(
        "crawling_urls_concurrently",
        url_count=len(urls),
    )

    semaphore = asyncio.Semaphore(settings.CRAWLER_MAX_CONCURRENCY)
    async with await create_async_client() as client:
        tasks = [
            _crawl_single_url(client, url, semaphore)
            for url in urls
        ]
        sources = await asyncio.gather(*tasks)

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