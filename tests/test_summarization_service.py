import pytest

from app.summarization.service import SummarizationService


@pytest.mark.anyio
async def test_summarization_service_returns_none_when_no_valid_sources():
    service = SummarizationService()

    summary, mode, sources, evidence_strength, evidence_warning = await service.summarize(
        query="ai agent frameworks",
        sources=[],
    )

    assert mode == "none"
    assert evidence_strength == "none"
    assert evidence_warning is not None
    assert "No readable source content" in summary
    assert sources == []


@pytest.mark.anyio
async def test_summarization_service_uses_fallback_when_llm_unavailable(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.OPENAI_API_KEY", None)

    service = SummarizationService()

    input_sources = [
        {
            "url": "https://example.com/agent-frameworks",
            "title": "AI Agent Frameworks",
            "content": "AI agent frameworks help agents plan, use tools, and maintain memory.",
            "word_count": 50,
            "extraction_quality": "medium",
            "extraction_quality_score": 0.7,
        }
    ]

    summary, mode, sources, evidence_strength, evidence_warning = await service.summarize(
        query="ai agent frameworks",
        sources=input_sources,
    )

    assert mode == "fallback"
    assert evidence_strength == "moderate"
    assert evidence_warning is not None
    assert "[1]" in summary
    assert sources[0]["citation_id"] == 1
    assert sources[0]["content_relevance_score"] > 0


@pytest.mark.anyio
async def test_summarization_service_assigns_citations_to_ranked_sources(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.OPENAI_API_KEY", None)

    service = SummarizationService()

    input_sources = [
        {
            "url": "https://example.com/weak",
            "title": "Cooking Article",
            "content": "This article is about cooking.",
            "word_count": 100,
            "extraction_quality": "medium",
            "extraction_quality_score": 0.7,
        },
        {
            "url": "https://example.com/strong",
            "title": "AI Agent Framework Guide",
            "content": "AI agent frameworks allow agents to plan tasks, call tools, and manage memory.",
            "word_count": 120,
            "extraction_quality": "medium",
            "extraction_quality_score": 0.7,
        },
    ]

    summary, mode, sources, evidence_strength, evidence_warning = await service.summarize(
        query="ai agent frameworks",
        sources=input_sources,
    )

    assert mode == "fallback"
    assert sources[0]["url"] == "https://example.com/strong"
    assert sources[0]["citation_id"] == 1
    assert sources[1]["citation_id"] == 2