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
from app.summarization.guardrails import assess_evidence_strength
from app.agent.sufficiency import check_source_sufficiency

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

    already_crawled_urls = {
        source.get("url")
        for source in state.get("sources", [])
    }

    urls = [
        url
        for url in urls
        if url not in already_crawled_urls
    ]

    if not urls:
        return {
            "sources": state.get("sources", [])
        }

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

    existing_sources = state.get("sources", [])

    return {

        "sources": existing_sources + blocked_sources + crawled_sources

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
    all_sources = ranked_sources + failed_or_unused_sources

    source_sufficiency = check_source_sufficiency(
        research_plan=state.get("research_plan", {}),
        sources=all_sources,
    )

    return {
        "summary": summary,
        "summary_mode": summary_mode,
        "sources": all_sources,
        "evidence_strength": evidence_strength,
        "evidence_warning": evidence_warning,
        "source_sufficiency": source_sufficiency,
    }

async def discover_urls(state: ResearchState) -> dict:
    if state["urls"]:
        return {
            "discovered_urls": state["urls"]
        }

    logger.info(
        "discovering_urls_from_research_plan",
        query=state["query"],
    )

    search_service = SearchService()

    research_plan = state.get("research_plan", {})
    search_queries = research_plan.get("search_queries") or None

    urls = await search_service.discover_urls(
        query=state["query"],
        max_results=settings.SEARCH_MAX_RESULTS,
        search_queries=search_queries,
    )

    existing_urls = state.get("discovered_urls", [])
    merged_urls = list(dict.fromkeys(existing_urls + urls))

    return {
        "discovered_urls": merged_urls
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

def assess_search_progress(state: ResearchState) -> dict:
    evidence_strength, evidence_warning = assess_evidence_strength(state["sources"])

    source_sufficiency = check_source_sufficiency(
        research_plan=state.get("research_plan", {}),
        sources=state["sources"],
    )

    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 2)

    should_continue = (
        not source_sufficiency["is_sufficient"]
        and iteration_count < max_iterations
        and not state["urls"]
    )

    logger.info(
        "search_progress_assessed",
        evidence_strength=evidence_strength,
        evidence_warning=evidence_warning,
        source_sufficiency=source_sufficiency,
        iteration_count=iteration_count,
        max_iterations=max_iterations,
        should_continue_search=should_continue,
    )

    return {
        "evidence_strength": evidence_strength,
        "evidence_warning": evidence_warning,
        "source_sufficiency": source_sufficiency,
        "should_continue_search": should_continue,
    }

def refine_research_plan(state: ResearchState) -> dict:
    research_plan = state.get("research_plan", {})
    original_query = state["query"]
    iteration_count = state.get("iteration_count", 0) + 1

    existing_queries = research_plan.get("search_queries", [])

    refined_queries = [
        f"{original_query} detailed comparison",
        f"{original_query} official documentation",
        f"{original_query} production use cases",
        f"{original_query} open source frameworks",
    ]

    merged_queries = list(dict.fromkeys(existing_queries + refined_queries))

    updated_plan = {
        **research_plan,
        "search_queries": merged_queries,
        "research_depth": "deepened",
    }

    logger.info(
        "research_plan_refined",
        iteration_count=iteration_count,
        search_query_count=len(merged_queries),
    )

    return {
        "research_plan": updated_plan,
        "iteration_count": iteration_count,
    }
