"""
Tavily web research tool with TTL caching.
Provides web search for recent news, transfers, injuries, and player updates.
Includes timeout handling and source attribution.
"""

from tavily import TavilyClient

from backend.config import settings
from backend.core.tools.cache import api_cache

_client = None


def _get_client() -> TavilyClient:
    """Lazy-initialize the Tavily client."""
    global _client
    if _client is None:
        if not settings.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY is not configured.")
        _client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    return _client


def tavily_search(query: str, max_results: int = 5) -> str:
    """
    Search the web via Tavily and return formatted text results with source tags.
    """
    if not query or not query.strip():
        return "No search query provided."

    cache_key = f"tavily_search_str_{query.strip().lower()}_{max_results}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        client = _get_client()
        response = client.search(
            query=query.strip(),
            search_depth="basic",
            max_results=max_results,
        )

        results = []
        for item in response.get("results", []):
            title = item.get("title", "Unknown")
            content = item.get("content", "No information available")
            url = item.get("url", "")

            results.append(
                f"""
[SOURCE: Web Research — Tavily]
Title: {title}
Information: {content}
Source URL: {url}
"""
            )

        if not results:
            res_str = "No web search results found."
        else:
            res_str = "\n".join(results)

        api_cache.set(cache_key, res_str)
        return res_str

    except ValueError as e:
        return f"Tavily configuration error: {str(e)}"
    except Exception as e:
        return f"Tavily search error: {str(e)}"


def tavily_search_structured(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web via Tavily and return structured dictionaries.
    """
    if not query or not query.strip():
        return []

    cache_key = f"tavily_search_struct_{query.strip().lower()}_{max_results}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        client = _get_client()
        response = client.search(
            query=query.strip(),
            search_depth="basic",
            max_results=max_results,
        )

        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", "Unknown"),
                "content": item.get("content", ""),
                "url": item.get("url", ""),
                "source": "Tavily Web Research",
            })

        api_cache.set(cache_key, results)
        return results

    except Exception:
        return []
