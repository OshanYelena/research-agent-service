from app.graph.nodes import assess_search_progress, refine_research_plan


def test_assess_search_progress_continues_when_evidence_weak():
    state = {
        "query": "latest AI agent frameworks",
        "urls": [],
        "sources": [
            {
                "content": "short",
                "extraction_quality": "very_low",
            }
        ],
        "iteration_count": 0,
        "max_iterations": 2,
    }

    result = assess_search_progress(state)

    assert result["evidence_strength"] == "weak"
    assert result["should_continue_search"] is True


def test_assess_search_progress_stops_when_max_iterations_reached():
    state = {
        "query": "latest AI agent frameworks",
        "urls": [],
        "sources": [
            {
                "content": "short",
                "extraction_quality": "very_low",
            }
        ],
        "iteration_count": 2,
        "max_iterations": 2,
    }

    result = assess_search_progress(state)

    assert result["should_continue_search"] is False


def test_refine_research_plan_adds_queries():
    state = {
        "query": "latest AI agent frameworks",
        "research_plan": {
            "search_queries": ["latest AI agent frameworks"]
        },
        "iteration_count": 0,
    }

    result = refine_research_plan(state)

    assert result["iteration_count"] == 1
    assert result["research_plan"]["research_depth"] == "deepened"
    assert len(result["research_plan"]["search_queries"]) > 1