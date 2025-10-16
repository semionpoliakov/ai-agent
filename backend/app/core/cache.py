from __future__ import annotations

import json
import asyncio
from hashlib import sha256
from typing import Any

import aioredis

from .config import get_settings

_settings = get_settings()
_redis: aioredis.Redis | None = None
_lock = asyncio.Lock()


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is not None:
        return _redis
    async with _lock:
        if _redis is not None:
            return _redis
        _redis = await aioredis.from_url(_settings.redis_url, encoding="utf-8", decode_responses=True)
        return _redis


def fingerprint(question: str, sql: str) -> str:
    normalized_sql = " ".join(sql.strip().split())
    payload = f"{question}\n{normalized_sql}".encode("utf-8")
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
