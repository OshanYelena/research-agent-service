from openai import AsyncOpenAI

from app.core.config import settings


class LLMClient:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")

        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL

    async def summarize_sources(
        self,
        query: str,
        sources: list[dict],
    ) -> str:
        source_blocks = []

        for fallback_index, source in enumerate(sources, start=1):
            citation_id = source.get("citation_id") or fallback_index
            title = source.get("title") or source.get("url")
            url = source.get("url")
            content = source.get("source_summary") or source.get("content") or ""

            source_blocks.append(
                f"""
SOURCE [{citation_id}]
Title: {title}
URL: {url}
Content:
{content[: settings.LLM_MAX_INPUT_CHARS]}
"""
            )

        prompt = f"""
You are a careful research summarization assistant.

User query:
{query}

Rules:
- Only use the provided source content.
- Do not invent facts.
- Use citations like [1], [2].
- If the sources are weak, incomplete, or unrelated, say so.
- Keep the answer concise and useful.

Sources:
{chr(10).join(source_blocks)}
"""

        response = await self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text