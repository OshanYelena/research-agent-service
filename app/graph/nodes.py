import asyncio

from app.core.config import settings
from app.core.logging import logger
from app.crawler.http_client import create_async_client, fetch_html_async
from app.crawler.extractor import extract_text_from_html
from app.graph.state import ResearchState
from app.crawler.summarizer import summarize_text_preview
from app.crawler.url_safety import deduplicate_urls, is_url_allowed
from app.search.service import SearchService
from app.summarization.service import SummarizationService
from app.agent.planner import create_research_plan



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


async def _crawl_single_url(
    client,
    url: str,
    semaphore: asyncio.Semaphore,
) -> dict:
    async with semaphore:
        status_code, html, error = await fetch_html_async(client, url)

        if error:
            return {
                "url": url,
                "status_code": status_code,
                "title": None,
                "content": None,
                "source_summary": None,
                "word_count": 0,
                "extraction_quality": "failed",
                "extraction_quality_score": 0.0,
                "error": error,
            }

        title, content, extraction_quality, extraction_quality_score = extract_text_from_html(html)

        word_count = len(content.split()) if content else 0
        source_summary = summarize_text_preview(content, max_words=80) if content else None

        if extraction_quality == "failed":
            error = "No readable content could be extracted from this page"
        else:
            error = None

        return {
            "url": url,
            "status_code": status_code,
            "title": title,
            "content": content,
            "source_summary": source_summary,
            "word_count": word_count,
            "extraction_quality": extraction_quality,
            "extraction_quality_score": extraction_quality_score,
            "error": error,
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
    service = SummarizationService()
    (
        summary,
        summary_mode,
        ranked_sources,
        evidence_strength,
        evidence_warning,
    ) = await service.summarize(
        query=state["query"],
        sources=state["sources"],
    )

    ranked_urls = {
        source.get("url")
        for source in ranked_sources
    }

    failed_or_unused_sources = [
        source
        for source in state["sources"]
        if source.get("url") not in ranked_urls
    ]

    return {
        "summary": summary,
        "summary_mode": summary_mode,
        "sources": ranked_sources + failed_or_unused_sources,
        "evidence_strength": evidence_strength,
        "evidence_warning": evidence_warning,
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

def plan_research(state: ResearchState) -> dict:
    plan = create_research_plan(state["query"])

    logger.info(
        "research_plan_created",
        intent=plan.intent,
        research_depth=plan.research_depth,
        needs_freshness=plan.needs_freshness,
        search_query_count=len(plan.search_queries),
    )

    return {
        "research_plan": plan.model_dump()
    }