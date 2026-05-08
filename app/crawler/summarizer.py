from app.graph import state


def summarize_text_preview(text: str, max_words: int = 80) -> str:
    words = text.split()

    if len(words) <= max_words:
        return text

    return " ".join(words[:max_words]) + "..."


def build_fallback_summary(sources: list[dict]) -> str:
    valid_sources = [
        source
        for source in sources
        if source.get("content") and source.get("extraction_quality") != "failed"
    ]

    if not valid_sources:
        return "No readable source content could be extracted from the provided URLs."

    summary_parts = []

    for index, source in enumerate(valid_sources, start=1):
        title = source.get("title") or source.get("url")
        source_summary = source.get("source_summary")

        if not source_summary:
            source_summary = summarize_text_preview(
                source.get("content", ""),
                max_words=80,
            )

        summary_parts.append(
            f"[{index}] {title}: {source_summary}"
        )

    return "\n\n".join(summary_parts)