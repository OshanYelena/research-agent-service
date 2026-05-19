from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError
from app.core.logging import logger


def _get_trace_id(request: Request) -> str | None:
    return getattr(request.state, "trace_id", None)


async def app_error_handler(request: Request, exc: AppError):
    trace_id = _get_trace_id(request)

    logger.warning(
        "app_error",
        trace_id=trace_id,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "trace_id": trace_id,
            }
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    trace_id = _get_trace_id(request)

    logger.warning(
        "http_error",
        trace_id=trace_id,
        status_code=exc.status_code,
        detail=exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": {},
                "trace_id": trace_id,
            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    trace_id = _get_trace_id(request)

    logger.warning(
        "validation_error",
        trace_id=trace_id,
        errors=exc.errors(),
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {
                    "errors": exc.errors(),
                },
                "trace_id": trace_id,
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    trace_id = _get_trace_id(request)

    logger.exception(
        "unhandled_error",
        trace_id=trace_id,
        error_type=type(exc).__name__,
        error=str(exc),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {},
                "trace_id": trace_id,
            }
        },
    )