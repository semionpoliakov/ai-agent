from __future__ import annotations

from hashlib import sha256
from typing import Any

from app.core.cache import fingerprint as make_fingerprint
from app.core.cache import read_cache, write_cache


def _question_key(question: str) -> str:
    digest = sha256(question.strip().lower().encode("utf-8")).hexdigest()
    return f"cache:question:{digest}"


def _fingerprint_key(question: str, sql: str) -> str:
    fingerprint = make_fingerprint(question, sql)
    return f"cache:fingerprint:{fingerprint}"


async def get_cached_response(question: str) -> dict[str, Any] | None:
    mapping = await read_cache(_question_key(question))
    if not mapping:
        return None
    fingerprint_key = mapping.get("fingerprint")
    if not fingerprint_key:
        return None
    return await read_cache(fingerprint_key)


async def store_response(question: str, sql: str, payload: dict[str, Any]) -> None:
    fingerprint_key = _fingerprint_key(question, sql)
    await write_cache(fingerprint_key, payload)
    await write_cache(_question_key(question), {"fingerprint": fingerprint_key})
