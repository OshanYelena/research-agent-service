from langgraph.graph import StateGraph, START, END

from app.graph.state import ResearchState
from app.graph.nodes import (
    create_search_plan,
    crawl_urls,
    summarize_sources,
)


def build_research_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("create_search_plan", create_search_plan)
    graph.add_node("crawl_urls", crawl_urls)
    graph.add_node("summarize_sources", summarize_sources)

    graph.add_edge(START, "create_search_plan")
    graph.add_edge("create_search_plan", "crawl_urls")
    graph.add_edge("crawl_urls", "summarize_sources")
    graph.add_edge("summarize_sources", END)

    return graph.compile()