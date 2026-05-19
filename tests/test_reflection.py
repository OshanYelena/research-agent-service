from app.agent.reflection import reflect_on_research_quality


def test_reflection_high_confidence():
    result = reflect_on_research_quality(
        evidence_strength="strong",
        source_sufficiency={"is_sufficient": True},
        source_conflicts={"has_conflict_signals": False},
    )

    assert result["confidence"] == "high"
    assert result["decision"] == "answer"


def test_reflection_medium_confidence_with_conflicts():
    result = reflect_on_research_quality(
        evidence_strength="strong",
        source_sufficiency={"is_sufficient": True},
        source_conflicts={"has_conflict_signals": True},
    )

    assert result["confidence"] == "medium"
    assert result["decision"] == "answer_with_caution"


def test_reflection_low_confidence_when_insufficient():
    result = reflect_on_research_quality(
        evidence_strength="weak",
        source_sufficiency={"is_sufficient": False},
        source_conflicts={"has_conflict_signals": False},
    )

    assert result["confidence"] == "low"
    assert result["decision"] == "answer_with_limitations"