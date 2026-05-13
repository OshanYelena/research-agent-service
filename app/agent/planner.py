from app.agent.models import ResearchPlan


def create_research_plan(query: str) -> ResearchPlan:
    cleaned_query = " ".join(query.split())

    lower_query = cleaned_query.lower()

    freshness_keywords = {
        "latest",
        "recent",
        "today",
        "news",
        "current",
        "new",
        "2026",
        "updated",
    }

    needs_freshness = any(keyword in lower_query for keyword in freshness_keywords)

    if needs_freshness:
        intent = "find_latest_information"
    elif "compare" in lower_query or "best" in lower_query:
        intent = "comparative_research"
    elif "how" in lower_query or "explain" in lower_query:
        intent = "explanatory_research"
    else:
        intent = "general_research"

    search_queries = [
        cleaned_query,
    ]

    if needs_freshness:
        search_queries.append(f"{cleaned_query} latest")
        search_queries.append(f"{cleaned_query} 2026")

    if "framework" in lower_query:
        search_queries.append(f"{cleaned_query} comparison")
        search_queries.append(f"{cleaned_query} examples")

    success_criteria = [
        "At least 2 usable sources should be extracted.",
        "Sources should be relevant to the user query.",
        "Final answer should include citations.",
    ]

    if needs_freshness:
        success_criteria.append("Prefer recent or updated sources.")

    return ResearchPlan(
        intent=intent,
        research_depth="standard",
        needs_freshness=needs_freshness,
        search_queries=list(dict.fromkeys(search_queries)),
        success_criteria=success_criteria,
    )