"""Redis cache adapter with JSON helpers and deterministic TTLs."""

from __future__ import annotations

import asyncio
from typing import Any, cast

from redis.asyncio import Redis

from ..config import Settings, get_settings
from ..serialization.json_utils import to_json

_REDIS_INSTANCE: Redis | None = None
_LOCK = asyncio.Lock()


async def get_redis(settings: Settings | None = None) -> Redis:
    """Return a cached Redis asyncio client."""
    settings = settings or get_settings()
    global _REDIS_INSTANCE
    if _REDIS_INSTANCE is not None:
        return _REDIS_INSTANCE
    async with _LOCK:
        if _REDIS_INSTANCE is None:
            _REDIS_INSTANCE = Redis.from_url(
                str(settings.redis_url),
                encoding="utf-8",
                decode_responses=True,
            )
    return _REDIS_INSTANCE


class RedisCache:
    """Typed helper for JSON cache access with a default TTL."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def read(self, key: str) -> dict[str, Any] | None:
        redis = await get_redis(self._settings)
        raw = await redis.get(key)
        if not raw:
            return None
        return cast(dict[str, Any], json.loads(raw))

    async def write(self, key: str, value: dict[str, Any], ttl_seconds: int | None = None) -> None:
        redis = await get_redis(self._settings)
        payload = to_json(value)
        expiry = ttl_seconds or self._settings.cache_ttl_seconds
        await redis.set(key, payload, ex=expiry)


_CACHE: RedisCache | None = None


def get_cache() -> RedisCache:
    """Return a process-wide RedisCache instance."""
    global _CACHE
    if _CACHE is None:
        _CACHE = RedisCache()
    return _CACHE
