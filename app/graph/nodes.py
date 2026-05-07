import asyncio

from app.core.config import settings
from app.core.logging import logger
from app.crawler.http_client import create_async_client, fetch_html_async
from app.crawler.extractor import extract_text_from_html
from app.graph.state import ResearchState
from app.crawler.summarizer import summarize_text_preview
from app.llm.client import LLMClient

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
        word_count = len(content.split()) if content else 0
        source_summary = summarize_text_preview(content, max_words=80) if content else None

        return {
            "url": url,
            "status_code": status_code,
            "title": title,
            "content": content,
            "source_summary": source_summary,
            "word_count": word_count,
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


async def summarize_sources(state: ResearchState) -> dict:
    valid_sources = [
        source for source in state["sources"]
        if source.get("content")
    ]

    if not valid_sources:
        return {
            "summary": "No readable source content could be extracted from the provided URLs."
        }

    logger.info(
        "summarizing_sources_with_llm",
        valid_source_count=len(valid_sources),
    )

    llm_client = LLMClient()
    summary = await llm_client.summarize_sources(
        query=state["query"],
        sources=valid_sources,
    )

    return {"summary": summary}