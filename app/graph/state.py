from typing import TypedDict


class SourceState(TypedDict, total=False):
    url: str
    status_code: int | None
    title: str | None
    content: str | None
    source_summary: str | None
    word_count: int | None
    error: str | None


class ResearchState(TypedDict):
    query: str
    urls: list[str]
    search_plan: str
    sources: list[SourceState]
    discovered_urls: list[str]
    summary: str
    summary_mode: str