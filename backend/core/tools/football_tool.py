"""
API-Football integration tool.
Provides structured player statistics, search, and details.
Features:
- Configurable season via environment variable
- Intelligent caching (TTL) and rate-limit mitigation
- Normalized player output schema
- Fallback handling for missing parameters
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from backend.config import settings
from backend.core.tools.cache import api_cache
from backend.core.tools.normalizer import normalize_player_record, deduplicate_players

TOP_LEAGUES = [
    39,   # Premier League
    140,  # La Liga
    78,   # Bundesliga
    135,  # Serie A
    61,   # Ligue 1
]

_session = requests.Session()
_retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
_session.mount("https://", HTTPAdapter(max_retries=_retry_strategy))

HEADERS = {"x-apisports-key": settings.FOOTBALL_API_KEY}
BASE_URL = settings.FOOTBALL_API_BASE_URL


def search_players_structured(query: str, season: int | None = None) -> list[dict]:
    """
    Search players via API-Football and return normalized dictionaries.
    Uses caching and deduplication.
    """
    if not query or not query.strip():
        return []

    if not settings.FOOTBALL_API_KEY:
        return []

    use_season = season or settings.FOOTBALL_SEASON
    cache_key = f"api_football_structured_{query.strip().lower()}_{use_season}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached

    url = f"{BASE_URL}/players"
    all_results = []

    for league_id in TOP_LEAGUES:
        params = {"search": query.strip(), "season": use_season, "league": league_id}
        try:
            resp = _session.get(url, headers=HEADERS, params=params, timeout=12)
            if resp.status_code == 429:
                continue
            resp.raise_for_status()
            league_data = resp.json()
            all_results.extend(league_data.get("response", []))
        except Exception:
            continue
        if len(all_results) >= 8:
            break

    players = []
    for item in all_results[:10]:
        player = item.get("player", {})
        statistics = item.get("statistics", [])
        stats = statistics[0] if statistics else {}
        games = stats.get("games", {})
        goals_data = stats.get("goals", {})
        cards = stats.get("cards", {})
        passes = stats.get("passes", {})
        shots = stats.get("shots", {})
        dribbles = stats.get("dribbles", {})
        tackles = stats.get("tackles", {})

        raw = {
            "id": player.get("id"),
            "name": player.get("name", "Unknown"),
            "firstname": player.get("firstname", ""),
            "lastname": player.get("lastname", ""),
            "age": player.get("age"),
            "nationality": player.get("nationality", "Unknown"),
            "birth_date": player.get("birth", {}).get("date"),
            "height": player.get("height"),
            "weight": player.get("weight"),
            "photo": player.get("photo", ""),
            "position": games.get("position", "Unknown"),
            "team": stats.get("team", {}).get("name", "Unknown"),
            "team_logo": stats.get("team", {}).get("logo", ""),
            "league": stats.get("league", {}).get("name", "Unknown"),
            "league_logo": stats.get("league", {}).get("logo", ""),
            "season": use_season,
            "appearances": games.get("appearences", 0) or 0,
            "minutes": games.get("minutes", 0) or 0,
            "rating": games.get("rating"),
            "goals": goals_data.get("total", 0) or 0,
            "assists": goals_data.get("assists", 0) or 0,
            "yellow_cards": cards.get("yellow", 0) or 0,
            "red_cards": cards.get("red", 0) or 0,
            "passes_accuracy": passes.get("accuracy"),
            "shots_total": shots.get("total", 0) or 0,
            "shots_on_target": shots.get("on", 0) or 0,
            "dribbles_success": dribbles.get("success", 0) or 0,
            "tackles_total": tackles.get("total", 0) or 0,
            "source": "API-Football",
        }
        players.append(normalize_player_record(raw, source="API-Football", default_season=use_season))

    deduped = deduplicate_players(players)
    api_cache.set(cache_key, deduped)
    return deduped


def search_players(query: str, season: int | None = None) -> str:
    """
    Search players via API-Football and return formatted string for LLM prompt context.
    """
    use_season = season or settings.FOOTBALL_SEASON
    structured = search_players_structured(query, use_season)

    if not structured:
        return f"No player data found for '{query}' in season {use_season}."

    players_text = []
    for p in structured:
        players_text.append(
            f"""
[SOURCE: API-Football — Season {p['season']}]
Player: {p['name']}
Full Name: {p['firstname']} {p['lastname']}
Player ID: {p['id']}
Age: {p['age']}
Date of Birth: {p['birth_date']}
Nationality: {p['nationality']}
Height: {p['height']}
Weight: {p['weight']}
Team: {p['team']}
League: {p['league']}
Position: {p['position']}
Appearances: {p['appearances']}
Minutes Played: {p['minutes']}
Rating: {p['rating']}
Goals: {p['goals']}
Assists: {p['assists']}
Shots (Total/On Target): {p['shots_total']}/{p['shots_on_target']}
Passes Accuracy: {p['passes_accuracy']}
Dribbles Successful: {p['dribbles_success']}
Tackles: {p['tackles_total']}
Yellow Cards: {p['yellow_cards']}
Red Cards: {p['red_cards']}
Photo: {p['photo']}
Team Logo: {p['team_logo']}
"""
        )

    return "\n".join(players_text)
