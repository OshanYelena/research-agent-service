from app.core.logging import logger
from app.llm.client import LLMClient
from app.summarization.fallback import build_fallback_summary


class SummarizationService:
    async def summarize(
        self,
        query: str,
        sources: list[dict],
    ) -> tuple[str, str]:
        valid_sources = [
            source
            for source in sources
            if source.get("content") and source.get("extraction_quality") != "failed"
        ]

        if not valid_sources:
            return (
                "No readable source content could be extracted from the provided URLs.",
                "none",
            )

        try:
            logger.info(
                "summarizing_sources_with_llm",
                valid_source_count=len(valid_sources),
            )

            llm_client = LLMClient()

            summary = await llm_client.summarize_sources(
                query=query,
                sources=valid_sources,
            )

            return summary, "llm"

        except Exception as exc:
            logger.warning(
                "llm_summary_failed_using_fallback",
                error=str(exc),
            )

            fallback_summary = build_fallback_summary(valid_sources)

            return fallback_summary, "fallback"