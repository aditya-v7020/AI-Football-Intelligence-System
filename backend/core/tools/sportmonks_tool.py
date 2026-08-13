"""
Sportmonks API tool integration.
Provides player lookups and detailed team/squad data.
Includes retry logic, caching, rate-limit awareness, and fallback handling.
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


def search_players_sportmonks(query: str) -> list[dict]:
    """
    Search for players via Sportmonks API v3.
    """
    if not query or not query.strip():
        return []

    if not settings.SPORTMONKS_API_KEY:
        return []

    cache_key = f"sportmonks_search_{query.strip().lower()}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached

    url = f"{settings.SPORTMONKS_BASE_URL}/players/search/{query.strip()}"
    params = {
        "api_token": settings.SPORTMONKS_API_KEY,
        "include": "teams;position;nationality",
    }

    try:
        resp = _session.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            api_cache.set(cache_key, [], ttl=300)
            return []

        data = resp.json().get("data", [])
        results = []
        for item in data[:5]:
            team_info = item.get("teams", [{}])[0] if item.get("teams") else {}
            pos_info = item.get("position", {}) or {}
            nat_info = item.get("nationality", {}) or {}

            raw = {
                "id": item.get("id"),
                "name": item.get("display_name") or item.get("common_name") or item.get("name"),
                "firstname": item.get("firstname"),
                "lastname": item.get("lastname"),
                "age": item.get("age"),
                "nationality": nat_info.get("name") if isinstance(nat_info, dict) else None,
                "birth_date": item.get("date_of_birth"),
                "height": f"{item.get('height')} cm" if item.get("height") else None,
                "weight": f"{item.get('weight')} kg" if item.get("weight") else None,
                "photo": item.get("image_path", ""),
                "position": pos_info.get("name") if isinstance(pos_info, dict) else "Unknown",
                "team": team_info.get("name") if isinstance(team_info, dict) else "Unknown",
                "league": "Sportmonks Data",
                "source": "Sportmonks",
            }
            results.append(normalize_player_record(raw, source="Sportmonks"))

        api_cache.set(cache_key, results)
        return results

    except Exception:
        api_cache.set(cache_key, [], ttl=300)
        return []
