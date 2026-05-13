def check_source_sufficiency(
    research_plan: dict,
    sources: list[dict],
) -> dict:
    usable_sources = [
        source
        for source in sources
        if source.get("content")
        and source.get("extraction_quality") in {"high", "medium", "low"}
    ]

    high_or_medium_sources = [
        source
        for source in usable_sources
        if source.get("extraction_quality") in {"high", "medium"}
    ]

    cited_sources = [
        source
        for source in sources
        if source.get("citation_id") is not None
    ]

    needs_freshness = research_plan.get("needs_freshness", False)

    has_minimum_usable_sources = len(usable_sources) >= 2
    has_minimum_quality_sources = len(high_or_medium_sources) >= 2
    has_citations = len(cited_sources) >= 1

    sufficient = (
        has_minimum_usable_sources
        and has_citations
        and (
            has_minimum_quality_sources
            if needs_freshness
            else True
        )
    )

    reasons = []

    if not has_minimum_usable_sources:
        reasons.append("Fewer than 2 usable sources were extracted.")

    if needs_freshness and not has_minimum_quality_sources:
        reasons.append("Fresh/latest research requires at least 2 high or medium quality sources.")

    if not has_citations:
        reasons.append("No cited sources are available yet.")

    if sufficient:
        reasons.append("Source sufficiency criteria are satisfied.")

    return {
        "is_sufficient": sufficient,
        "usable_source_count": len(usable_sources),
        "quality_source_count": len(high_or_medium_sources),
        "cited_source_count": len(cited_sources),
        "reasons": reasons,
    }