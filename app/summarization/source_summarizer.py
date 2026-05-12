from app.crawler.summarizer import summarize_text_preview


def build_source_summary(source: dict, max_words: int = 120) -> str | None:
    content = source.get("content")

    if not content:
        return None

    return summarize_text_preview(content, max_words=max_words)


def attach_source_summaries(sources: list[dict]) -> list[dict]:
    enriched_sources = []

    for source in sources:
        if source.get("source_summary"):
            enriched_sources.append(source)
            continue

        source_summary = build_source_summary(source)

        enriched_sources.append(
            {
                **source,
                "source_summary": source_summary,
            }
        )

    return enriched_sources