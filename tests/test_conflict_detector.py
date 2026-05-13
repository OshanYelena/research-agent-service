from app.agent.conflict_detector import detect_source_conflicts


def test_detect_source_conflicts_returns_false_for_no_conflicts():
    result = detect_source_conflicts(
        [
            {
                "url": "https://example.com/a",
                "title": "AI Agent Frameworks",
                "source_summary": "This article explains AI agent frameworks clearly.",
                "citation_id": 1,
            }
        ]
    )

    assert result["has_conflict_signals"] is False
    assert result["conflict_source_count"] == 0


def test_detect_source_conflicts_detects_keywords():
    result = detect_source_conflicts(
        [
            {
                "url": "https://example.com/a",
                "title": "Framework Comparison",
                "source_summary": "Unlike other frameworks, this tool performs differently.",
                "citation_id": 1,
            }
        ]
    )

    assert result["has_conflict_signals"] is True
    assert result["conflict_source_count"] == 1
    assert result["conflict_sources"][0]["citation_id"] == 1