from uuid import uuid4

from fastapi import APIRouter, Request

from app.core.tracing import get_tracer
from app.graph.workflow import build_research_graph
from app.schemas.research import ResearchRequest, ResearchResponse, SourceResult

from app.core.metrics import (
    RESEARCH_REQUEST_COUNT,
    RESEARCH_SOURCE_COUNT,
    RESEARCH_FAILED_SOURCE_COUNT,

)

router = APIRouter(prefix="/research", tags=["research"])

research_graph = build_research_graph()
tracer = get_tracer(__name__)

@router.post("", response_model=ResearchResponse)
async def research(
    request_body: ResearchRequest,
    request: Request,
):
    trace_id = getattr(request.state, "trace_id", str(uuid4()))

    with tracer.start_as_current_span("research_graph.invoke") as span:
        span.set_attribute("research.query", request_body.query)
        span.set_attribute("research.url_count", len(request_body.urls))

        result = await research_graph.ainvoke(
            {
                "query": request_body.query,
                "urls": [str(url) for url in request_body.urls],
                "search_plan": "",
                "sources": [],
                "summary": "",
                "summary_mode": "none",
                "discovered_urls": [],
                "evidence_strength": "none",
                "evidence_warning": None,
                "research_plan": {},
                "iteration_count": 0,
                "max_iterations": 2,
                "source_sufficiency": {},
                "should_continue_search": False,
                "source_conflicts": {},
            }
        )

        span.set_attribute("research.source_count", len(result["sources"]))
        span.set_attribute("research.summary_mode", result["summary_mode"])

    source_count = len(result["sources"])
    failed_source_count = len(
        [
            source for source in result["sources"]
            if source.get("error")
        ]
    )

    sources = [
        SourceResult(
            url=source["url"],
            status_code=source.get("status_code"),
            title=source.get("title"),
            content_preview=source.get("content", "")[:300] if source.get("content") else None,
            source_summary=source.get("source_summary"),
            word_count=source.get("word_count"),
            error=source.get("error"),
            extraction_quality=source.get("extraction_quality"),
            extraction_quality_score=source.get("extraction_quality_score"),
            content_relevance_score=source.get("content_relevance_score"),
            citation_id=source.get("citation_id"),
        )
        for source in result["sources"]
    ]

    RESEARCH_REQUEST_COUNT.labels(
        summary_mode=result["summary_mode"],
        evidence_strength=result.get("evidence_strength", "none"),
    ).inc()

    RESEARCH_SOURCE_COUNT.observe(source_count)
    RESEARCH_FAILED_SOURCE_COUNT.observe(failed_source_count)

    return ResearchResponse(
        trace_id=trace_id,
        query=result["query"],
        search_plan=result["search_plan"],
        summary=result["summary"],
        summary_mode=result["summary_mode"],
        evidence_strength=result["evidence_strength"],
        evidence_warning=result.get("evidence_warning"),
        source_count=source_count,
        failed_source_count=failed_source_count,
        sources=sources,
        processing_time_ms=None,
        research_plan=result.get("research_plan", {}),
        source_sufficiency=result.get("source_sufficiency", {}),
        source_conflicts=result.get("source_conflicts", {}),
    )