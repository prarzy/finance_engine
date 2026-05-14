import time
import threading


class TTLCache:
    """Simple thread-safe in-memory TTL cache."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> str | None:
        """
        Get a value from the cache if it exists and hasn't expired.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value or None if not found or expired.
        """
        with self._lock:
            if key in self._store:
                value, expires_at = self._store[key]
                if time.time() < expires_at:
                    return value
                del self._store[key]
        return None

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        """
        Set a value in the cache with a time-to-live.
        
        Args:
            key: Cache key.
            value: Value to cache (must be string).
            ttl_seconds: Time-to-live in seconds.
        """
        with self._lock:
            self._store[key] = (value, time.time() + ttl_seconds)

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._store.clear()


fx_cache = TTLCache()
