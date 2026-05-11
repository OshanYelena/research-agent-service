from app.core.logging import logger
from app.llm.client import LLMClient
from app.summarization.fallback import build_fallback_summary


class FinalSynthesizer:
    async def synthesize(
            self,
            query: str,
            sources: list[dict],
            evidence_strength: str,
            evidence_warning: str | None,
    ) -> tuple[str, str]:
        try:
            logger.info(
                "running_final_synthesis",
                source_count=len(sources),
            )

            llm_client = LLMClient()

            summary = await llm_client.summarize_sources(
                query=query,
                sources=sources,
                evidence_strength=evidence_strength,
                evidence_warning=evidence_warning,
            )

            return summary, "llm"

        except Exception as exc:
            logger.warning(
                "final_synthesis_failed_using_fallback",
                error=str(exc),
            )

            return build_fallback_summary(sources), "fallback"