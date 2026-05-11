from app.summarization.guardrails import assess_evidence_strength


def test_evidence_strength_none():
    strength, warning = assess_evidence_strength([])

    assert strength == "none"
    assert warning is not None


def test_evidence_strength_weak():
    sources = [
        {
            "content": "short content",
            "extraction_quality": "very_low",
        }
    ]

    strength, warning = assess_evidence_strength(sources)

    assert strength == "weak"
    assert "low" in warning.lower()


def test_evidence_strength_moderate():
    sources = [
        {
            "content": "good content",
            "extraction_quality": "high",
        }
    ]

    strength, warning = assess_evidence_strength(sources)

    assert strength == "moderate"


def test_evidence_strength_strong():
    sources = [
        {
            "content": "good content one",
            "extraction_quality": "high",
        },
        {
            "content": "good content two",
            "extraction_quality": "medium",
        },
    ]

    strength, warning = assess_evidence_strength(sources)

    assert strength == "strong"