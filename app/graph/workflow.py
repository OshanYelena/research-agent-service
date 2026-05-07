from langgraph.graph import StateGraph, START, END
from app.graph.state import ResearchState
from app.graph.nodes import (
    create_search_plan,
    mock_extract_sources,
    summarize_notes,
)

def build_research_graph():

    graph = StateGraph(ResearchState)
    graph.add_node("create_search_plan", create_search_plan)
    graph.add_node("mock_extract_sources", mock_extract_sources)
    graph.add_node("summarize_notes", summarize_notes)
    graph.add_edge(START, "create_search_plan")
    graph.add_edge("create_search_plan", "mock_extract_sources")
    graph.add_edge("mock_extract_sources", "summarize_notes")
    graph.add_edge("summarize_notes", END)

    return graph.compile()