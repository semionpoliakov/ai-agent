"""SQL safety checks applied before executing LLM generated statements."""

from __future__ import annotations

import re
from typing import Final

FORBIDDEN_KEYWORDS: Final[tuple[str, ...]] = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "ALTER",
    "DROP",
    "TRUNCATE",
    "ATTACH",
    "DETACH",
    "OPTIMIZE",
    "SYSTEM",
    "GRANT",
    "REVOKE",
    "MERGE",
    "KILL",
    "CREATE",
)

COMMENT_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(--.*?$)|(/\*.*?\*/)", re.MULTILINE | re.DOTALL
)
STRING_PATTERN: Final[re.Pattern[str]] = re.compile(r"'([^']|'')*'")


def _strip_comments(sql: str) -> str:
    return re.sub(COMMENT_PATTERN, " ", sql)


def _mask_string_literals(sql: str) -> str:
    return re.sub(STRING_PATTERN, "''", sql)


def validate_sql_is_safe(sql: str) -> str:
    """Ensure the SQL statement is a single SELECT without dangerous constructs."""
    if COMMENT_PATTERN.search(sql):
        raise ValueError("SQL comments are not permitted")

    cleaned = _strip_comments(sql).strip()
    if not cleaned:
        raise ValueError("SQL query is empty")

    normalized = " ".join(cleaned.split())
    if not normalized.upper().startswith("SELECT"):
        raise ValueError("Only SELECT statements are permitted")

    if normalized.endswith(";"):
        raise ValueError("Trailing semicolons are not permitted")

    masked = _mask_string_literals(normalized.upper())

    if ";" in masked[:-1]:
        raise ValueError("Multiple statements are not allowed")

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", masked, flags=re.IGNORECASE):
            raise ValueError(f"Forbidden keyword detected: {keyword}")

    return normalized
