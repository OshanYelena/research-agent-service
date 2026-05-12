from app.summarization.source_summarizer import (
    attach_source_summaries,
    build_source_summary,
)


def test_build_source_summary_returns_summary():
    source = {
        "content": " ".join(["word"] * 200)
    }

    summary = build_source_summary(source, max_words=50)

    assert summary is not None
    assert len(summary.split()) <= 51


def test_attach_source_summaries_adds_missing_summary():
    sources = [
        {
            "url": "https://example.com",
            "content": "This is useful extracted content.",
        }
    ]

    result = attach_source_summaries(sources)

    assert result[0]["source_summary"] is not None


def test_attach_source_summaries_preserves_existing_summary():
    sources = [
        {
            "url": "https://example.com",
            "content": "Full content.",
            "source_summary": "Existing summary.",
        }
    ]

    result = attach_source_summaries(sources)

    assert result[0]["source_summary"] == "Existing summary."