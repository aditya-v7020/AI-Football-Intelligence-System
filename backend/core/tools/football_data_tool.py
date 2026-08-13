"""
Football-Data.org API tool integration.
Provides standings, fixtures, results, and team squad data.
Uses X-Auth-Token for authentication with caching and retry logic.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from backend.config import settings
from backend.core.tools.cache import api_cache
from backend.core.tools.normalizer import normalize_player_record

_session = requests.Session()
_retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503], allowed_methods=["GET"])
_session.mount("https://", HTTPAdapter(max_retries=_retry))

TOP_COMPETITIONS = ["PL", "PD", "BL1", "SA", "FL1"]  # Premier League, La Liga, Bundesliga, Serie A, Ligue 1


def _get_headers() -> dict:
    return {"X-Auth-Token": settings.FOOTBALL_DATA_API_KEY}


def get_standings(competition_code: str = "PL") -> str:
    """
    Get standings for a competition from Football-Data.org.
    """
    if not settings.FOOTBALL_DATA_API_KEY:
        return "Football-Data.org API key is not configured."

    code = competition_code.upper()
    cache_key = f"football_data_standings_{code}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached

    url = f"{settings.FOOTBALL_DATA_BASE_URL}/competitions/{code}/standings"
    try:
        resp = _session.get(url, headers=_get_headers(), timeout=10)
        if resp.status_code != 200:
            msg = f"Unable to fetch standings for {code} (HTTP {resp.status_code})"
            api_cache.set(cache_key, msg, ttl=300)
            return msg

        data = resp.json()
        comp_name = data.get("competition", {}).get("name", code)
        standings = data.get("standings", [])
        if not standings:
            return f"No standings found for {comp_name}."

        table = standings[0].get("table", [])
        lines = [f"[SOURCE: Football-Data.org — Competition: {comp_name}]"]
        for row in table[:10]:
            pos = row.get("position")
            team = row.get("team", {}).get("name", "Unknown")
            played = row.get("playedGames", 0)
            won = row.get("won", 0)
            draw = row.get("draw", 0)
            lost = row.get("lost", 0)
            pts = row.get("points", 0)
            lines.append(f"{pos}. {team} | P:{played} W:{won} D:{draw} L:{lost} Pts:{pts}")

        result = "\n".join(lines)
        api_cache.set(cache_key, result, ttl=1800)
        return result

    except Exception as e:
        err_msg = f"Football-Data.org standings error: {str(e)}"
        api_cache.set(cache_key, err_msg, ttl=300)
        return err_msg


def get_fixtures(competition_code: str = "PL") -> str:
    """
    Get recent and upcoming fixtures for a competition.
    """
    if not settings.FOOTBALL_DATA_API_KEY:
        return "Football-Data.org API key is not configured."

    code = competition_code.upper()
    cache_key = f"football_data_fixtures_{code}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached

    url = f"{settings.FOOTBALL_DATA_BASE_URL}/competitions/{code}/matches"
    try:
        resp = _session.get(url, headers=_get_headers(), params={"limit": 10}, timeout=10)
        if resp.status_code != 200:
            msg = f"Unable to fetch fixtures for {code}"
            api_cache.set(cache_key, msg, ttl=300)
            return msg

        matches = resp.json().get("matches", [])
        if not matches:
            return f"No match fixtures found for {code}."

        lines = [f"[SOURCE: Football-Data.org — Matches/Fixtures for {code}]"]
        for m in matches[:8]:
            home = m.get("homeTeam", {}).get("name", "Home")
            away = m.get("awayTeam", {}).get("name", "Away")
            status = m.get("status", "SCHEDULED")
            score = m.get("score", {}).get("fullTime", {})
            h_score = score.get("home") if score.get("home") is not None else "-"
            a_score = score.get("away") if score.get("away") is not None else "-"
            date = m.get("utcDate", "")[:10]
            lines.append(f"{date} | {home} {h_score} - {a_score} {away} ({status})")

        result = "\n".join(lines)
        api_cache.set(cache_key, result, ttl=1800)
        return result

    except Exception as e:
        return f"Football-Data.org fixtures error: {str(e)}"


def get_squad_players_football_data(competition_code: str = "PL") -> list[dict]:
    """
    Fetch players from top competition teams (for scouting real candidates).
    """
    if not settings.FOOTBALL_DATA_API_KEY:
        return []

    cache_key = f"football_data_squads_{competition_code}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached

    url = f"{settings.FOOTBALL_DATA_BASE_URL}/competitions/{competition_code}/teams"
    try:
        resp = _session.get(url, headers=_get_headers(), timeout=10)
        if resp.status_code != 200:
            return []

        teams = resp.json().get("teams", [])
        players = []

        for team in teams[:6]:
            team_name = team.get("name", "Unknown")
            squad = team.get("squad", [])
            for p in squad:
                raw = {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "nationality": p.get("nationality"),
                    "birth_date": p.get("dateOfBirth"),
                    "position": p.get("position", "Unknown"),
                    "team": team_name,
                    "league": competition_code,
                    "source": "Football-Data.org",
                }
                players.append(normalize_player_record(raw, source="Football-Data.org"))

        api_cache.set(cache_key, players, ttl=3600)
        return players

    except Exception:
        return []
