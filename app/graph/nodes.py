from app.graph.state import ResearchState
from app.core.logging import logger


def create_search_plan(state: ResearchState) -> dict:
    query = state["query"]

    logger.info(
        "creating_search_plan",
        query=query,
    )

    return {
        "search_plan": f"Search the web for reliable information about: {query}"
    }


def mock_extract_sources(state: ResearchState) -> dict:
    logger.info(
        "extracting_mock_sources",
        query=state["query"],
    )

    return {
        "extracted_notes": [
            f"Mock source note 1 related to {state['query']}",
            f"Mock source note 2 related to {state['query']}",
        ]
    }


def summarize_notes(state: ResearchState) -> dict:
    logger.info("summarizing_notes")

    notes = state["extracted_notes"]

    return {
        "summary": " ".join(notes)
    }