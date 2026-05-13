from langgraph.graph import StateGraph, START, END

from app.graph.state import ResearchState
from app.graph.nodes import (
    create_search_plan,
    crawl_urls,
    summarize_sources,
    discover_urls,
    plan_research,
)


def build_research_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("plan_research", plan_research)
    graph.add_node("create_search_plan", create_search_plan)
    graph.add_node("discover_urls", discover_urls)
    graph.add_node("crawl_urls", crawl_urls)
    graph.add_node("summarize_sources", summarize_sources)

    graph.add_edge(START, "plan_research")
    graph.add_edge("plan_research", "create_search_plan")
    graph.add_edge("create_search_plan", "discover_urls")
    graph.add_edge("discover_urls", "crawl_urls")
    graph.add_edge("crawl_urls", "summarize_sources")
    graph.add_edge("summarize_sources", END)

    return graph.compile()