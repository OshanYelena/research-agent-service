from typing import TypedDict


class ResearchState(TypedDict):
    query: str
    search_plan: str
    extracted_notes: list[str]
    summary: str


