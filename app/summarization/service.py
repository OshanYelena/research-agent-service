from app.summarization.relevance import rank_sources_by_relevance
from app.summarization.source_summarizer import attach_source_summaries
from app.summarization.synthesizer import FinalSynthesizer


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

        synthesizer = FinalSynthesizer()

        summary, summary_mode = await synthesizer.synthesize(
            query=query,
            sources=ranked_sources,
        )

        return summary, summary_mode, ranked_sources