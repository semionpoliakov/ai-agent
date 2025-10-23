"""Validation helpers ensuring ClickHouse queries stay read-only and safe."""

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

FORBIDDEN_PATTERN: Final[re.Pattern[str]] = re.compile(
    rf"\b({'|'.join(FORBIDDEN_KEYWORDS)})\b",
    flags=re.IGNORECASE,
)

COMMENT_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(--.*?$)|(/\*.*?\*/)", re.MULTILINE | re.DOTALL
)
STRING_PATTERN: Final[re.Pattern[str]] = re.compile(r"'([^']|'')*'")


def _strip_comments(sql: str) -> str:
    return re.sub(COMMENT_PATTERN, " ", sql)


def _mask_string_literals(sql: str) -> str:
    return re.sub(STRING_PATTERN, "''", sql)


def validate_clickhouse_sql(sql: str) -> str:
    """Ensure the SQL statement is a single read-only SELECT."""
    if not sql or not sql.strip():
        raise ValueError("SQL query is empty")

    if COMMENT_PATTERN.search(sql):
        raise ValueError("SQL comments are not permitted")

    cleaned = _strip_comments(sql).strip()
    normalized = " ".join(cleaned.split())

    normalized_upper = normalized.upper()

    masked = _mask_string_literals(normalized_upper)

    if FORBIDDEN_PATTERN.search(masked):
        raise ValueError("Forbidden SQL operation detected")

    if not normalized_upper.startswith("SELECT"):
        raise ValueError("Only SELECT statements are permitted")

    if normalized.endswith(";"):
        raise ValueError("Trailing semicolons are not permitted")

    if ";" in masked[:-1]:
        raise ValueError("Multiple statements are not allowed")

    return normalized
