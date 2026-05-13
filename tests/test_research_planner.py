from app.agent.planner import create_research_plan


def test_create_research_plan_detects_freshness():
    plan = create_research_plan("latest AI agent frameworks")

    assert plan.intent == "find_latest_information"
    assert plan.needs_freshness is True
    assert len(plan.search_queries) >= 2


def test_create_research_plan_for_general_query():
    plan = create_research_plan("explain AI agents")

    assert plan.intent == "explanatory_research"
    assert plan.research_depth == "standard"
    assert plan.success_criteria