from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.research import router as research_router

app = FastAPI(
    title="Research Agent Service",
    version="0.0.1",
    description="Standalone LangGraph-powered web research agent service.",
)

app.include_router(health_router)
app.include_router(research_router)