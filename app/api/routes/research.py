from fastapi import APIRouter
from uuid import uuid4
from app.graph.workflow import build_research_graph
from app.schemas.research import ResearchRequest, ResearchResponse, SourceResult

router = APIRouter(prefix="/research", tags=["research"])

research_graph = build_research_graph()


@router.post("", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    trace_id = str(uuid4())

    result = await research_graph.ainvoke(
        {
            "query": request.query,
            "urls": [str(url) for url in request.urls],
            "search_plan": "",
            "sources": [],
            "summary": "",
            "summary_mode": "none",
            "discovered_urls": [],
        }
    )

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

    return ResearchResponse(
        trace_id=trace_id,
        query=result["query"],
        search_plan=result["search_plan"],
        summary=result["summary"],
        summary_mode=result["summary_mode"],
        source_count=source_count,
        failed_source_count=failed_source_count,
        sources=sources,
    )