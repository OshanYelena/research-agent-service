from fastapi import APIRouter

from app.graph.workflow import build_research_graph
from app.schemas.research import ResearchRequest, ResearchResponse, SourceResult

router = APIRouter(prefix="/research", tags=["research"])

research_graph = build_research_graph()


@router.post("", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    result = await research_graph.ainvoke(
        {
            "query": request.query,
            "urls": [str(url) for url in request.urls],
            "search_plan": "",
            "sources": [],
            "summary": "",
        }
    )

    sources = [
        SourceResult(
            url=source["url"],
            status_code=source.get("status_code"),
            title=source.get("title"),
            content_preview=source.get("content", "")[:300] if source.get("content") else None,
            error=source.get("error"),
        )
        for source in result["sources"]
    ]

    return ResearchResponse(
        query=result["query"],
        search_plan=result["search_plan"],
        summary=result["summary"],
        sources=sources,
    )