"""
TheSportsDB API tool integration.
Provides player bio, images (cutout/thumb), team info, and profile fallback.
Includes caching, retry logic, and fallback handling.
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


def search_players_thesportsdb(query: str) -> list[dict]:
    """
    Search for player profile and images via TheSportsDB API.
    """
    if not query or not query.strip():
        return []

    key = settings.THESPORTSDB_API_KEY or "123"
    cache_key = f"thesportsdb_player_{query.strip().lower()}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached

    url = f"{settings.THESPORTSDB_BASE_URL}/{key}/searchplayers.php"
    params = {"p": query.strip()}

    try:
        resp = _session.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            api_cache.set(cache_key, [], ttl=300)
            return []

        data = resp.json().get("player")
        if not data:
            api_cache.set(cache_key, [], ttl=300)
            return []

        results = []
        for p in data[:5]:
            raw = {
                "id": p.get("idPlayer"),
                "name": p.get("strPlayer"),
                "nationality": p.get("strNationality"),
                "birth_date": p.get("dateBorn"),
                "height": p.get("strHeight"),
                "weight": p.get("strWeight"),
                "photo": p.get("strCutout") or p.get("strThumb") or p.get("strRender") or "",
                "position": p.get("strPosition"),
                "team": p.get("strTeam"),
                "league": p.get("strLeague"),
                "description": p.get("strDescriptionEN"),
                "source": "TheSportsDB",
            }
            results.append(normalize_player_record(raw, source="TheSportsDB"))

        api_cache.set(cache_key, results)
        return results

    except Exception:
        api_cache.set(cache_key, [], ttl=300)
        return []
