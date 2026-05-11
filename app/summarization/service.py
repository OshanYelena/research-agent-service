from app.core.logging import logger
from app.llm.client import LLMClient
from app.summarization.fallback import build_fallback_summary
from app.summarization.relevance import rank_sources_by_relevance
from app.summarization.source_summarizer import attach_source_summaries


class SummarizationService:
    async def summarize(
            self,
            query: str,
            sources: list[dict],
    ) -> tuple[str, str, list[dict]]:
        valid_sources = [
            source
            for source in sources
            if source.get("content") and source.get("extraction_quality") != "failed"
        ]

        if not valid_sources:
            return (
                "No readable source content could be extracted from the provided URLs.",
                "none",
                sources,
            )

        ranked_sources = rank_sources_by_relevance(
            query=query,
            sources=valid_sources,
        )

        ranked_sources = attach_source_summaries(ranked_sources)

        try:
            logger.info(
                "summarizing_sources_with_llm",
                valid_source_count=len(ranked_sources),
            )

            llm_client = LLMClient()

            summary = await llm_client.summarize_sources(
                query=query,
                sources=ranked_sources,
            )

            return summary, "llm", ranked_sources

        except Exception as exc:
            logger.warning(
                "llm_summary_failed_using_fallback",
                error=str(exc),
            )

            fallback_summary = build_fallback_summary(ranked_sources)

            return fallback_summary, "fallback", ranked_sources