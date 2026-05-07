from pydantic import BaseModel, Field, HttpUrl


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    urls: list[HttpUrl] = Field(default_factory=list, max_length=5)


class SourceResult(BaseModel):
    url: str
    status_code: int | None = None
    title: str | None = None
    content_preview: str | None = None
    error: str | None = None


class ResearchResponse(BaseModel):
    query: str
    search_plan: str
    summary: str
    sources: list[SourceResult]