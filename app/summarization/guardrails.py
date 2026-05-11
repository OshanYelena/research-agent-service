def assess_evidence_strength(sources: list[dict]) -> tuple[str, str]:
    usable_sources = [
        source
        for source in sources
        if source.get("content") and source.get("extraction_quality") != "failed"
    ]

    if not usable_sources:
        return "none", "No usable source content was available."

    high_quality_count = len(
        [
            source
            for source in usable_sources
            if source.get("extraction_quality") in {"high", "medium"}
        ]
    )

    low_quality_count = len(
        [
            source
            for source in usable_sources
            if source.get("extraction_quality") in {"low", "very_low"}
        ]
    )

    if high_quality_count >= 2:
        return "strong", "Multiple high/medium quality sources are available."

    if high_quality_count == 1:
        return "moderate", "Only one high/medium quality source is available."

    if low_quality_count > 0:
        return "weak", "Only low or very-low quality extracted sources are available."

    return "none", "No reliable evidence was available."