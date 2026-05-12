import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.core.config import settings
from app.core.logging import logger

T = TypeVar("T")


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    operation_name: str,
) -> T:
    last_error: Exception | None = None

    for attempt in range(1, settings.LLM_MAX_RETRIES + 2):
        try:
            return await operation()

        except Exception as exc:
            last_error = exc

            logger.warning(
                "async_operation_failed",
                operation_name=operation_name,
                attempt=attempt,
                max_attempts=settings.LLM_MAX_RETRIES + 1,
                error_type=type(exc).__name__,
                error=str(exc) or repr(exc),
            )

            if attempt > settings.LLM_MAX_RETRIES:
                break

            await asyncio.sleep(0.5 * attempt)

    raise last_error