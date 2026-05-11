from app.crawler.summarizer import summarize_text_preview


def build_fallback_summary(sources: list[dict]) -> str:
    valid_sources = [
        source
        for source in sources
        if source.get("content") and source.get("extraction_quality") != "failed"
    ]

    if not valid_sources:
        return "No readable source content could be extracted from the provided URLs."

    summary_parts = []

    for fallback_index, source in enumerate(valid_sources, start=1):
        citation_id = source.get("citation_id") or fallback_index
        title = source.get("title") or source.get("url")
        source_summary = source.get("source_summary")

        if not source_summary:
            source_summary = summarize_text_preview(
                source.get("content", ""),
                max_words=80,
            )

        summary_parts.append(f"[{citation_id}] {title}: {source_summary}")

    return "\n\n".join(summary_parts)