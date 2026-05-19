import time
from uuid import uuid4
import asyncio
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.core.metrics import REQUEST_COUNT, REQUEST_LATENCY
from app.core.rate_limiter import rate_limiter


class RequestMetadataMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid4())
        start_time = time.perf_counter()
        rate_limit_remaining: int | None = None

        request.state.trace_id = trace_id

        client_host = request.client.host if request.client else "unknown"

        logger.info(
            "request_started",
            trace_id=trace_id,
            method=request.method,
            path=request.url.path,
            client_host=client_host,
        )

        if settings.RATE_LIMIT_ENABLED and request.url.path == "/research":
            allowed, rate_limit_remaining = rate_limiter.is_allowed(client_host)

            if not allowed:
                processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

                logger.warning(
                    "rate_limit_exceeded",
                    trace_id=trace_id,
                    client_host=client_host,
                    path=request.url.path,
                )

                REQUEST_COUNT.labels(
                    method=request.method,
                    path=request.url.path,
                    status_code="429",
                ).inc()

                REQUEST_LATENCY.labels(
                    method=request.method,
                    path=request.url.path,
                ).observe(processing_time_ms / 1000)

                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests. Please try again later.",
                            "details": {
                                "limit": settings.RATE_LIMIT_REQUESTS,
                                "window_seconds": settings.RATE_LIMIT_WINDOW_SECONDS,
                            },
                            "trace_id": trace_id,
                        }
                    },
                    headers={
                        "X-Trace-Id": trace_id,
                        "X-Processing-Time-Ms": str(processing_time_ms),
                        "X-RateLimit-Remaining": str(rate_limit_remaining),
                    },
                )

        try:
            response = await asyncio.wait_for(
                call_next(request),
                timeout=settings.REQUEST_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

            logger.warning(
                "request_timeout",
                trace_id=trace_id,
                method=request.method,
                path=request.url.path,
                timeout_seconds=settings.REQUEST_TIMEOUT_SECONDS,
            )

            REQUEST_COUNT.labels(
                method=request.method,
                path=request.url.path,
                status_code="504",
            ).inc()

            REQUEST_LATENCY.labels(
                method=request.method,
                path=request.url.path,
            ).observe(processing_time_ms / 1000)

            return JSONResponse(
                status_code=504,
                content={
                    "error": {
                        "code": "REQUEST_TIMEOUT",
                        "message": "Request exceeded the configured timeout budget.",
                        "details": {
                            "timeout_seconds": settings.REQUEST_TIMEOUT_SECONDS,
                        },
                        "trace_id": trace_id,
                    }
                },
                headers={
                    "X-Trace-Id": trace_id,
                    "X-Processing-Time-Ms": str(processing_time_ms),
                },
            )

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        REQUEST_COUNT.labels(
            method=request.method,
            path=request.url.path,
            status_code=str(response.status_code),
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            path=request.url.path,
        ).observe(processing_time_ms / 1000)

        response.headers["X-Trace-Id"] = trace_id
        response.headers["X-Processing-Time-Ms"] = str(processing_time_ms)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        if rate_limit_remaining is not None:
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_remaining)

        logger.info(
            "request_completed",
            trace_id=trace_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            processing_time_ms=processing_time_ms,
            rate_limit_remaining=rate_limit_remaining,
        )

        return response