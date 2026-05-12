import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class RequestMetadataMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid4())
        start_time = time.perf_counter()

        request.state.trace_id = trace_id

        logger.info(
            "request_started",
            trace_id=trace_id,
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["X-Trace-Id"] = trace_id
        response.headers["X-Processing-Time-Ms"] = str(processing_time_ms)

        logger.info(
            "request_completed",
            trace_id=trace_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            processing_time_ms=processing_time_ms,
        )

        return response