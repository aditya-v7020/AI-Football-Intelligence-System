"""
Player API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from backend.models.schemas import (
    PlayerSearchResponse,
    ComparisonRequest,
    ComparisonResponse,
)
from backend.services.player_service import search_player, get_player_news
from backend.services.comparison_service import compare_players

router = APIRouter(prefix="/api/players", tags=["Players"])


@router.get("/search", response_model=PlayerSearchResponse)
async def search(
    q: str = Query(..., min_length=1, max_length=200, description="Player name to search"),
    season: int | None = Query(None, description="Season year (e.g. 2024)")
):
    """Search for football players via API-Football."""
    q = q.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    try:
        result = await search_player(q, season)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Player search failed: {str(e)}")


@router.get("/news")
async def player_news(
    name: str = Query(..., min_length=1, max_length=200, description="Player name")
):
    """Get recent news about a player via web research."""
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Player name cannot be empty.")

    try:
        news = await get_player_news(name)
        return {"player": name, "news": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News retrieval failed: {str(e)}")


@router.post("/compare", response_model=ComparisonResponse)
async def compare(request: ComparisonRequest):
    """Compare two football players with AI analysis."""
    p1 = request.player1.strip()
    p2 = request.player2.strip()

    if not p1 or not p2:
        raise HTTPException(status_code=400, detail="Both player names are required.")

    if p1.lower() == p2.lower():
        raise HTTPException(status_code=400, detail="Please enter two different players to compare.")

    try:
        result = await compare_players(p1, p2)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")
