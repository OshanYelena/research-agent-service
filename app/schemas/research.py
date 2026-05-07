from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)


class ResearchResponse(BaseModel):
    query: str
    search_plan: str
    summary: str
    extracted_notes: list[str]