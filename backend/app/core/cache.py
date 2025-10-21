from __future__ import annotations

import asyncio
import json
from hashlib import sha256
from typing import Any

from redis.asyncio import Redis

from .config import get_settings

_settings = get_settings()
_redis: Redis | None = None
_lock = asyncio.Lock()


async def get_redis() -> Redis:
    global _redis
    if _redis is not None:
        return _redis
    async with _lock:
        if _redis is None:
            _redis = Redis.from_url(
                str(_settings.redis_url),
                encoding="utf-8",
                decode_responses=True,
            )
    return _redis


def fingerprint(question: str, sql: str) -> str:
    normalized_sql = " ".join(sql.strip().split())
    payload = f"{question}\n{normalized_sql}".encode()
    return sha256(payload).hexdigest()


async def read_cache(key: str) -> dict[str, Any] | None:
    redis = await get_redis()
    raw = await redis.get(key)
    if not raw:
        return None
    return json.loads(raw)


async def write_cache(key: str, value: dict[str, Any]) -> None:
    redis = await get_redis()
    await redis.set(key, json.dumps(value), ex=_settings.cache_ttl_seconds)
