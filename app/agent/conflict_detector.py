CONFLICT_KEYWORDS = {
    "however",
    "but",
    "although",
    "despite",
    "contrary",
    "conflict",
    "disagree",
    "different",
    "whereas",
    "unlike",
    "versus",
    "vs",
}


def detect_source_conflicts(sources: list[dict]) -> dict:
    usable_sources = [
        source
        for source in sources
        if source.get("source_summary") or source.get("content")
    ]

    conflict_sources = []

    for source in usable_sources:
        text = f"{source.get('title') or ''} {source.get('source_summary') or source.get('content') or ''}".lower()

        matched_keywords = [
            keyword
            for keyword in CONFLICT_KEYWORDS
            if keyword in text
        ]

        if matched_keywords:
            conflict_sources.append(
                {
                    "url": source.get("url"),
                    "title": source.get("title"),
                    "citation_id": source.get("citation_id"),
                    "matched_keywords": matched_keywords,
                }
            )

    has_conflict_signals = len(conflict_sources) > 0

    return {
        "has_conflict_signals": has_conflict_signals,
        "conflict_source_count": len(conflict_sources),
        "conflict_sources": conflict_sources,
    }