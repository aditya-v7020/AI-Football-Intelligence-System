"""
Intelligent Multi-Source Football Data Pipeline.
Coordinates data retrieval across API-Football, Sportmonks, TheSportsDB,
Football-Data.org, and Tavily with intelligent routing, fallbacks, and deduplication.
"""

from typing import Optional

from backend.config import settings
from backend.core.tools.football_tool import search_players_structured, search_players
from backend.core.tools.sportmonks_tool import search_players_sportmonks
from backend.core.tools.thesportsdb_tool import search_players_thesportsdb
from backend.core.tools.football_data_tool import (
    get_standings,
    get_fixtures,
    get_squad_players_football_data,
)
from backend.core.tools.tavily_tool import tavily_search
from backend.core.tools.normalizer import deduplicate_players


def get_multi_source_player_data(query: str, season: Optional[int] = None) -> tuple[str, list[dict], list[str]]:
    """
    Intelligently query player data across multiple sources with fallback & deduplication.
    Returns:
      - formatted_text: String prompt for LLM context
      - structured_players: List of normalized player dicts
      - sources_used: List of data source names queried
    """
    if not query or not query.strip():
        return "No player query specified.", [], []

    use_season = season or settings.FOOTBALL_SEASON
    sources_used = []
    all_players = []

    # Primary structured source: API-Football
    api_football_players = search_players_structured(query, season=use_season)
    if api_football_players:
        all_players.extend(api_football_players)
        sources_used.append("API-Football")

    # Fallback / Enrichment: Sportmonks if API-Football returned few/no results
    if len(all_players) < 2 and settings.SPORTMONKS_API_KEY:
        sportmonks_players = search_players_sportmonks(query)
        if sportmonks_players:
            all_players.extend(sportmonks_players)
            sources_used.append("Sportmonks")

    # Fallback / Profile Enrichment: TheSportsDB
    if len(all_players) == 0 or any(not p.get("photo") for p in all_players):
        thesportsdb_players = search_players_thesportsdb(query)
        if thesportsdb_players:
            all_players.extend(thesportsdb_players)
            sources_used.append("TheSportsDB")

    deduped = deduplicate_players(all_players)

    if not deduped:
        return f"No player data found across sources for '{query}'.", [], sources_used

    # Build prompt string
    prompt_parts = []
    for p in deduped:
        prompt_parts.append(
            f"""
[SOURCE: {p.get('source', 'Multi-Source')}]
Player: {p['name']}
Team: {p['team']}
League: {p['league']}
Position: {p['position']}
Age: {p['age'] or 'Not available'}
Nationality: {p['nationality']}
Goals: {p['goals']} | Assists: {p['assists']}
Rating: {p['rating']} | Appearances: {p['appearances']}
Pass Accuracy: {p['passes_accuracy']} | Dribbles: {p['dribbles_success']} | Tackles: {p['tackles_total']}
Photo: {p['photo']}
"""
        )

    return "\n".join(prompt_parts), deduped, sources_used


def get_multi_source_competition_data(query: str) -> tuple[str, list[str]]:
    """
    Query competition standings, fixtures, or league tables if relevant.
    """
    q_lower = query.lower()
    sources_used = []
    results = []

    # Map keywords to Football-Data.org codes
    comp_map = {
        "premier league": "PL",
        "epl": "PL",
        "la liga": "PD",
        "bundesliga": "BL1",
        "serie a": "SA",
        "ligue 1": "FL1",
    }

    selected_code = "PL"
    for keyword, code in comp_map.items():
        if keyword in q_lower:
            selected_code = code
            break

    if any(kw in q_lower for kw in ["standings", "table", "rankings", "leaderboard", "points"]):
        standings_text = get_standings(selected_code)
        results.append(standings_text)
        sources_used.append("Football-Data.org (Standings)")

    if any(kw in q_lower for kw in ["fixture", "matches", "schedule", "games", "results", "score"]):
        fixtures_text = get_fixtures(selected_code)
        results.append(fixtures_text)
        sources_used.append("Football-Data.org (Fixtures)")

    return "\n\n".join(results), sources_used


def get_real_scout_candidates(
    position: str = "Midfielder",
    reference_player_name: Optional[str] = None
) -> tuple[list[dict], list[str]]:
    """
    Retrieve real candidate players from top leagues using APIs for scouting comparison.
    Ensures zero LLM statistics/player hallucinations.
    """
    sources_used = []
    candidates = []

    # 1. If reference player specified, search for reference player first
    ref_player = None
    if reference_player_name:
        _, ref_list, ref_sources = get_multi_source_player_data(reference_player_name)
        if ref_list:
            ref_player = ref_list[0]
            sources_used.extend(ref_sources)

    # Determine position to search
    target_pos = position
    if ref_player and ref_player.get("position") != "Not available":
        target_pos = ref_player.get("position")

    # 2. Retrieve real candidate players from top leagues via Football-Data & API-Football
    squad_players = get_squad_players_football_data("PL") + get_squad_players_football_data("PD")
    if squad_players:
        sources_used.append("Football-Data.org Squads")

    # Filter candidates matching position
    for p in squad_players:
        p_pos = p.get("position", "").lower()
        if target_pos.lower() in p_pos or p_pos in target_pos.lower() or "midfield" in p_pos:
            if ref_player and p.get("name", "").lower() == ref_player.get("name", "").lower():
                continue
            candidates.append(p)
            if len(candidates) >= 8:
                break

    # Fallback to search if candidates are sparse
    if len(candidates) < 3:
        for term in ["De Bruyne", "Bellingham", "Pedri", "Odegaard", "Rice", "Modric", "Barella", "Valverde"]:
            _, found, _ = get_multi_source_player_data(term)
            if found:
                p = found[0]
                if not ref_player or p.get("name", "").lower() != ref_player.get("name", "").lower():
                    candidates.append(p)
            if len(candidates) >= 6:
                break

    deduped = deduplicate_players(candidates)
    return deduped, list(set(sources_used))
