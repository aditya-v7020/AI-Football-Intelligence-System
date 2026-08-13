"""
Thread-safe TTL in-memory cache for API responses.
Prevents duplicate external HTTP calls and helps stay within API rate limits.
"""

import time
import threading
from typing import Any, Optional

from backend.config import settings


class SimpleTTLCache:
    """Thread-safe TTL cache store."""

    def __init__(self, default_ttl: int = settings.CACHE_TTL_SECONDS):
        self.default_ttl = default_ttl
        self._cache: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None
            expiry, value = self._cache[key]
            if time.time() > expiry:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if value is None:
            return
        use_ttl = ttl if ttl is not None else self.default_ttl
        expiry = time.time() + use_ttl
        with self._lock:
            self._cache[key] = (expiry, value)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


# Global cache instance for tools
api_cache = SimpleTTLCache()
