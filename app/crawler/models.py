from pydantic import BaseModel, HttpUrl


class CrawledPage(BaseModel):
    url: str
    status_code: int | None = None
    title: str | None = None
    content: str | None = None
    error: str | None = None