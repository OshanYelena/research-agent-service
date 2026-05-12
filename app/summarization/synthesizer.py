from app.core.logging import logger
from app.llm.client import LLMClient
from app.summarization.fallback import build_fallback_summary
from app.summarization.retry import retry_async


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
                evidence_strength=evidence_strength,
            )

            llm_client = LLMClient()

            async def run_llm_summary() -> str:
                return await llm_client.summarize_sources(
                    query=query,
                    sources=sources,
                    evidence_strength=evidence_strength,
                    evidence_warning=evidence_warning,
                )

            summary = await retry_async(
                operation=run_llm_summary,
                operation_name="final_synthesis",
            )

            return summary, "llm"

        except Exception as exc:
            logger.warning(
                "final_synthesis_failed_using_fallback",
                error_type=type(exc).__name__,
                error=str(exc) or repr(exc),
            )

            return build_fallback_summary(sources), "fallback"