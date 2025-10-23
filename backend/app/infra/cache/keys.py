"""Key builders for Redis cache entries."""

from __future__ import annotations

from hashlib import sha256


def normalize_sql(sql: str) -> str:
    """Collapse whitespace to produce a canonical SQL representation."""
    return " ".join(sql.strip().split())


def fingerprint(question: str, sql: str) -> str:
    normalized_sql = normalize_sql(sql)
    payload = f"{question}\n{normalized_sql}".encode()
    return sha256(payload).hexdigest()


def question_key(question: str) -> str:
    digest = sha256(question.strip().lower().encode("utf-8")).hexdigest()
    return f"cache:question:{digest}"


def fingerprint_key(question: str, sql: str) -> str:
    return f"cache:fingerprint:{fingerprint(question, sql)}"
