"""Redis cache adapter with JSON helpers and deterministic TTLs."""

from __future__ import annotations

import json
from typing import Any, cast

from redis.asyncio import Redis

from ..config import Settings, get_settings
from ..serialization.json_utils import to_json


class RedisCache:
    """Typed helper for JSON cache access with a default TTL."""

    def __init__(self, redis: Redis, settings: Settings | None = None) -> None:
        self._redis = redis
        self._settings = settings or get_settings()

    @property
    def redis(self) -> Redis:
        return self._redis

    async def read(self, key: str) -> dict[str, Any] | None:
        raw = await self._redis.get(key)
        if not raw:
            return None
        return cast(dict[str, Any], json.loads(raw))

    async def write(self, key: str, value: dict[str, Any], ttl_seconds: int | None = None) -> None:
        payload = to_json(value)
        expiry = ttl_seconds or self._settings.cache_ttl_seconds
        await self._redis.set(key, payload, ex=expiry)
