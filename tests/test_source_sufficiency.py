from app.agent.sufficiency import check_source_sufficiency


def test_source_sufficiency_fails_with_no_sources():
    result = check_source_sufficiency(
        research_plan={"needs_freshness": False},
        sources=[],
    )

    assert result["is_sufficient"] is False
    assert result["usable_source_count"] == 0


def test_source_sufficiency_passes_for_general_research_with_two_usable_sources():
    result = check_source_sufficiency(
        research_plan={"needs_freshness": False},
        sources=[
            {
                "content": "useful content",
                "extraction_quality": "low",
                "citation_id": 1,
            },
            {
                "content": "more useful content",
                "extraction_quality": "low",
                "citation_id": 2,
            },
        ],
    )

    assert result["is_sufficient"] is True


def test_source_sufficiency_requires_quality_for_fresh_research():
    result = check_source_sufficiency(
        research_plan={"needs_freshness": True},
        sources=[
            {
                "content": "weak content",
                "extraction_quality": "low",
                "citation_id": 1,
            },
            {
                "content": "weak content",
                "extraction_quality": "low",
                "citation_id": 2,
            },
        ],
    )

    assert result["is_sufficient"] is False
    assert result["quality_source_count"] == 0


def test_source_sufficiency_passes_for_fresh_research_with_two_quality_sources():
    result = check_source_sufficiency(
        research_plan={"needs_freshness": True},
        sources=[
            {
                "content": "good content",
                "extraction_quality": "high",
                "citation_id": 1,
            },
            {
                "content": "medium content",
                "extraction_quality": "medium",
                "citation_id": 2,
            },
        ],
    )

    assert result["is_sufficient"] is True