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

        for index, source in enumerate(sources, start=1):
            title = source.get("title") or source.get("url")
            url = source.get("url")
            content = source.get("content") or ""

            source_blocks.append(
                f"""
SOURCE [{index}]
Title: {title}
URL: {url}
Content:
{content[: settings.LLM_MAX_INPUT_CHARS]}
"""
            )

        prompt = f"""
You are a research summarization assistant.

User query:
{query}

Summarize the provided sources.

Rules:
- Only use the provided source content.
- Do not invent facts.
- Mention source numbers like [1], [2] when making claims.
- If sources are weak or incomplete, say so.
- Give a concise but useful answer.

Sources:
{chr(10).join(source_blocks)}
"""

        response = await self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text