"""
Player and Statistics Normalizer & Deduplicator.
Normalizes data from API-Football, Sportmonks, TheSportsDB, Football-Data.org, and Tavily
into a single standardized schema, handling missing fields and removing duplicates.
"""

import re
from typing import Any, Optional


def normalize_string(text: Optional[str], default: str = "Not available") -> str:
    """Normalize text values cleanly."""
    if not text or not str(text).strip():
        return default
    val = str(text).strip()
    return default if val.lower() in ["none", "null", "unknown", "n/a", ""] else val


def normalize_int(val: Any, default: int = 0) -> int:
    """Normalize integer statistics cleanly."""
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def normalize_player_record(
    raw: dict,
    source: str,
    default_season: int = 2024
) -> dict:
    """
    Standardize a player dictionary into the system's common schema.
    """
    name = normalize_string(raw.get("name") or raw.get("strPlayer"), "Unknown Player")
    team = normalize_string(raw.get("team") or raw.get("strTeam"), "Not available")
    position = normalize_string(raw.get("position") or raw.get("strPosition"), "Not available")
    nationality = normalize_string(raw.get("nationality") or raw.get("strNationality"), "Not available")
    league = normalize_string(raw.get("league") or raw.get("strLeague"), "Not available")
    photo = raw.get("photo") or raw.get("strThumb") or raw.get("strCutout") or ""

    return {
        "id": raw.get("id"),
        "name": name,
        "firstname": normalize_string(raw.get("firstname") or raw.get("first_name"), ""),
        "lastname": normalize_string(raw.get("lastname") or raw.get("last_name"), ""),
        "age": raw.get("age"),
        "nationality": nationality,
        "birth_date": normalize_string(raw.get("birth_date") or raw.get("dateBorn"), "Not available"),
        "height": normalize_string(raw.get("height") or raw.get("strHeight"), "Not available"),
        "weight": normalize_string(raw.get("weight") or raw.get("strWeight"), "Not available"),
        "photo": photo if str(photo).startswith("http") else "",
        "position": position,
        "team": team,
        "team_logo": raw.get("team_logo", ""),
        "league": league,
        "league_logo": raw.get("league_logo", ""),
        "season": raw.get("season") or default_season,
        "appearances": normalize_int(raw.get("appearances")),
        "minutes": normalize_int(raw.get("minutes")),
        "rating": normalize_string(str(raw.get("rating")) if raw.get("rating") else None, "N/A"),
        "goals": normalize_int(raw.get("goals")),
        "assists": normalize_int(raw.get("assists")),
        "yellow_cards": normalize_int(raw.get("yellow_cards")),
        "red_cards": normalize_int(raw.get("red_cards")),
        "passes_accuracy": normalize_string(str(raw.get("passes_accuracy")) if raw.get("passes_accuracy") else None, "N/A"),
        "shots_total": normalize_int(raw.get("shots_total")),
        "shots_on_target": normalize_int(raw.get("shots_on_target")),
        "dribbles_success": normalize_int(raw.get("dribbles_success")),
        "tackles_total": normalize_int(raw.get("tackles_total")),
        "source": source,
    }


def _clean_key_string(text: str) -> str:
    """Helper to convert player name into simple key for deduplication."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def deduplicate_players(players: list[dict]) -> list[dict]:
    """
    Deduplicate player records based on normalized name and team/nationality.
    Merges missing fields (e.g. photos, bios) from secondary sources into primary records.
    """
    seen: dict[str, dict] = {}
    result: list[dict] = []

    for p in players:
        name_key = _clean_key_string(p.get("name", ""))
        if not name_key:
            continue

        # If already seen, merge fields if current primary lacks photo/details
        if name_key in seen:
            existing = seen[name_key]
            # Merge photo if existing is missing it
            if not existing.get("photo") and p.get("photo"):
                existing["photo"] = p["photo"]
            # Merge sources used list
            existing_sources = existing.get("source", "")
            if p.get("source") and p["source"] not in existing_sources:
                existing["source"] = f"{existing_sources}, {p['source']}"
            continue

        seen[name_key] = dict(p)
        result.append(seen[name_key])

    return result
