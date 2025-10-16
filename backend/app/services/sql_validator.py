from __future__ import annotations

import re
from typing import Final

_ILLEGAL_KEYWORDS: Final[tuple[str, ...]] = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "TRUNCATE",
    "ALTER",
    "CREATE",
    "RENAME",
    "ATTACH",
    "DETACH",
    "MERGE",
    "GRANT",
    "REVOKE",
    "SYSTEM",
    "KILL",
    "OPTIMIZE",
    "USE",
    "SET",
)

_COMMENT_PATTERN: Final[re.Pattern[str]] = re.compile(r"(--.*?$)|(/\*.*?\*/)", re.MULTILINE | re.DOTALL)


def _strip_comments(sql: str) -> str:
    return re.sub(_COMMENT_PATTERN, " ", sql)


def allow_only_select(sql: str) -> str:
    """Ensure the SQL statement is a single SELECT query."""
    cleaned = _strip_comments(sql).strip()
    if not cleaned:
        raise ValueError("SQL query is empty")

    normalized = " ".join(cleaned.split())
    if not normalized.upper().startswith("SELECT"):
        raise ValueError("Only SELECT statements are permitted")

    uppercase = normalized.upper()
    if any(keyword in uppercase for keyword in _ILLEGAL_KEYWORDS):
        raise ValueError("Query contains forbidden keywords")

    if ";" in normalized[:-1]:
        raise ValueError("Multiple statements are not allowed")

    return normalized
