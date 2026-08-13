"""
AI Scout API endpoints.
"""

from fastapi import APIRouter, HTTPException
from backend.models.schemas import ScoutRequest, ScoutResponse
from backend.services.scout_service import run_scout

router = APIRouter(prefix="/api/scout", tags=["Scout"])


@router.post("", response_model=ScoutResponse)
async def scout(request: ScoutRequest):
    """
    Run AI scouting with natural language requirements.
    Uses the full multi-agent pipeline to find matching players.
    """
    requirements = request.requirements.strip()

    if not requirements:
        raise HTTPException(status_code=400, detail="Scouting requirements cannot be empty.")

    try:
        result = await run_scout(requirements, request.thread_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scouting failed: {str(e)}")
