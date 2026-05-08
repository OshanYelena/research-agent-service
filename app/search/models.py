from pydantic import BaseModel, HttpUrl


class SearchResult(BaseModel):
    title: str | None = None
    url: HttpUrl
    snippet: str | None = None
    source: str
    rank: int | None = None