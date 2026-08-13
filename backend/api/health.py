"""
Health check & diagnostic API endpoints.
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
    db_status = "connected" if db_ok else ("memory_fallback" if not settings.DATABASE_URL else "disconnected")

    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        database=db_status,
        groq_configured=bool(settings.GROQ_API_KEY),
        tavily_configured=bool(settings.TAVILY_API_KEY),
        football_api_configured=bool(settings.FOOTBALL_API_KEY),
        sportmonks_configured=bool(settings.SPORTMONKS_API_KEY),
        thesportsdb_configured=bool(settings.THESPORTSDB_API_KEY),
        football_data_configured=bool(settings.FOOTBALL_DATA_API_KEY),
        football_season=settings.FOOTBALL_SEASON,
    )


@router.get("/system-status")
async def system_status():
    """
    Safe diagnostic system status endpoint for production environment inspection.
    Never exposes API secrets.
    """
    db_ok = check_db_health()
    return {
        "backend": "ok",
        "database": "connected" if db_ok else ("memory_fallback" if not settings.DATABASE_URL else "disconnected"),
        "groq": "configured" if bool(settings.GROQ_API_KEY) else "not_configured",
        "api_football": "configured" if bool(settings.FOOTBALL_API_KEY) else "not_configured",
        "sportmonks": "configured" if bool(settings.SPORTMONKS_API_KEY) else "not_configured",
        "thesportsdb": "configured" if bool(settings.THESPORTSDB_API_KEY) else "not_configured",
        "football_data": "configured" if bool(settings.FOOTBALL_DATA_API_KEY) else "not_configured",
        "tavily": "configured" if bool(settings.TAVILY_API_KEY) else "not_configured",
        "football_season": settings.FOOTBALL_SEASON,
    }
