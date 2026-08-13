"""
Player service — handles multi-source player searches and profile lookups.
"""

from backend.core.tools.multi_source_pipeline import get_multi_source_player_data
from backend.core.tools.tavily_tool import tavily_search_structured
from backend.models.schemas import PlayerData, PlayerSearchResponse
from backend.config import settings


async def search_player(query: str, season: int | None = None) -> PlayerSearchResponse:
    """Search for players across multi-source APIs."""
    use_season = season or settings.FOOTBALL_SEASON
    _, raw_players, sources = get_multi_source_player_data(query, use_season)

    players = [PlayerData(**p) for p in raw_players]

    return PlayerSearchResponse(
        query=query,
        season=use_season,
        players=players,
        sources=sources,
        total=len(players),
    )


async def get_player_news(player_name: str) -> list[dict]:
    """Get recent news about a player via Tavily."""
    query = f"Latest football news about {player_name} 2024 2025"
    return tavily_search_structured(query, max_results=5)
