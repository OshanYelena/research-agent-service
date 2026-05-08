import asyncio

from app.core.config import settings
from app.core.logging import logger
from app.crawler.http_client import create_async_client, fetch_html_async
from app.crawler.extractor import extract_text_from_html
from app.graph.state import ResearchState
from app.crawler.summarizer import summarize_text_preview, build_fallback_summary
from app.llm.client import LLMClient
from app.crawler.url_safety import deduplicate_urls, is_url_allowed
from app.search.service import SearchService




def create_search_plan(state: ResearchState) -> dict:

    query = state["query"]
    url_count = len(state["urls"])
    if url_count > 0:
        plan = f"Crawl {url_count} user-provided URLs and summarize information related to: {query}"
    else:
        plan = f"Discover relevant URLs for query, crawl them, and summarize information related to: {query}"

    logger.info(
        "creating_search_plan",
        query=query,
        user_url_count=url_count,
    )

    return {
        "search_plan": plan
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

        title, content, extraction_error = extract_text_from_html(html)

        if extraction_error:
            return {
                "url": url,
                "status_code": status_code,
                "title": title,
                "content": content,
                "source_summary": None,
                "word_count": len(content.split()) if content else 0,
                "error": extraction_error,
            }

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
    urls = deduplicate_urls(state["discovered_urls"])

    if not urls:
        return {"sources": []}

    safe_urls = []
    blocked_sources = []

    for url in urls:
        allowed, reason = is_url_allowed(url)

        if allowed:
            safe_urls.append(url)
        else:
            blocked_sources.append(
                {
                    "url": url,
                    "status_code": None,
                    "title": None,
                    "content": None,
                    "source_summary": None,
                    "word_count": 0,
                    "error": reason,
                }
            )

    if not safe_urls:
        return {"sources": blocked_sources}

    logger.info(
        "crawling_safe_urls_concurrently",
        url_count=len(safe_urls),
        blocked_url_count=len(blocked_sources),
    )

    semaphore = asyncio.Semaphore(settings.CRAWLER_MAX_CONCURRENCY)

    async with await create_async_client() as client:
        tasks = [
            _crawl_single_url(client, url, semaphore)
            for url in safe_urls
        ]

        crawled_sources = await asyncio.gather(*tasks)

    return {
        "sources": blocked_sources + crawled_sources
    }


async def summarize_sources(state: ResearchState) -> dict:

    valid_sources = [
        source for source in state["sources"]
        if source.get("content")
    ]

    if not valid_sources:
        return {
            "summary": "No readable source content could be extracted from the provided URLs.",
            "summary_mode": "none",
        }

    try:

        logger.info(
            "summarizing_sources_with_llm",
            valid_source_count=len(valid_sources),
        )

        llm_client = LLMClient()

        summary = await llm_client.summarize_sources(
            query=state["query"],
            sources=valid_sources,
        )
        return {
            "summary": summary,
            "summary_mode": "llm",
        }

    except Exception as exc:

        logger.warning(
            "llm_summary_failed_using_fallback",
            error=str(exc),

        )
        fallback_summary = build_fallback_summary(valid_sources)
        return {
            "summary": fallback_summary,
            "summary_mode": "fallback",
        }

async def discover_urls(state: ResearchState) -> dict:
    if state["urls"]:
        return {
            "discovered_urls": state["urls"]
        }

    logger.info(
        "discovering_urls_from_query",
        query=state["query"],
    )

    search_service = SearchService()

    urls = await search_service.discover_urls(
        query=state["query"],
        max_results=settings.SEARCH_MAX_RESULTS,
    )

    return {
        "discovered_urls": urls
    }