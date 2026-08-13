"""
Health check API endpoint.
"""

from fastapi import APIRouter
from backend.models.schemas import HealthResponse
from backend.core.graph import check_db_health
from backend.config import settings

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    System health check — reports configuration status of all 5 data APIs + PostgreSQL + Groq.
    """
    db_ok = check_db_health()

    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        database="connected" if db_ok else "disconnected",
        groq_configured=bool(settings.GROQ_API_KEY),
        tavily_configured=bool(settings.TAVILY_API_KEY),
        football_api_configured=bool(settings.FOOTBALL_API_KEY),
        sportmonks_configured=bool(settings.SPORTMONKS_API_KEY),
        thesportsdb_configured=bool(settings.THESPORTSDB_API_KEY),
        football_data_configured=bool(settings.FOOTBALL_DATA_API_KEY),
        football_season=settings.FOOTBALL_SEASON,
    )
