from fastapi import APIRouter

from app.graph.workflow import build_research_graph
from app.schemas.research import ResearchRequest, ResearchResponse

router = APIRouter(prefix="/research", tags=["research"])
research_graph = build_research_graph()

@router.post("", response_model=ResearchResponse)
def research(request: ResearchRequest):
    result = research_graph.invoke(
        {
            "query": request.query,
            "search_plan": "",
            "extracted_notes": [],
            "summary": "",
        }
    )

    return ResearchResponse(
        query=result["query"],
        search_plan=result["search_plan"],
        extracted_notes=result["extracted_notes"],
        summary=result["summary"],
    )