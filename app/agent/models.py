from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    intent: str = Field(default="general_research")
    research_depth: str = Field(default="standard")
    needs_freshness: bool = False
    search_queries: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)