from app.graph.state import ResearchState


def create_search_plan(state: ResearchState):
    query = state["query"]

    return {
        "search_plan": f"Search the web for reliable information about: {query}"
    }


def mock_extract_sources(state: ResearchState) -> dict:
    return {
        "extracted_notes": [
            f"Mock source note 1 related to {state['query']}",
            f"Mock source note 2 related to {state['query']}",
        ]
    }


def summarize_notes(state: ResearchState) -> dict:
    notes = state["extracted_notes"]
    return {
        "summary": " ".join(notes)
    }