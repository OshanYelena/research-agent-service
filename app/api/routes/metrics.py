from fastapi import APIRouter, Response

from app.core.metrics import render_metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def metrics():
    content, content_type = render_metrics()

    return Response(
        content=content,
        media_type=content_type,
    )