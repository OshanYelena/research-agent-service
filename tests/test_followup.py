from app.agent.followup import generate_follow_up_question


def test_follow_up_none_for_high_confidence():
    question = generate_follow_up_question(
        query="ai agent frameworks",
        research_reflection={
            "confidence": "high",
            "decision": "answer",
        },
        source_sufficiency={
            "reasons": ["Source sufficiency criteria are satisfied."]
        },
    )

    assert question is None


def test_follow_up_for_limited_sources():
    question = generate_follow_up_question(
        query="ai agent frameworks",
        research_reflection={
            "confidence": "low",
            "decision": "answer_with_limitations",
        },
        source_sufficiency={
            "reasons": ["Fewer than 2 usable sources were extracted."]
        },
    )

    assert question is not None
    assert "broaden" in question.lower()


def test_follow_up_for_medium_confidence():
    question = generate_follow_up_question(
        query="ai agent frameworks",
        research_reflection={
            "confidence": "medium",
            "decision": "answer_with_caution",
        },
        source_sufficiency={
            "reasons": []
        },
    )

    assert question is not None
    assert "deeper comparison" in question.lower()