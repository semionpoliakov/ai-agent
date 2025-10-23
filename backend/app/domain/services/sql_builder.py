"""Helpers to normalise SQL text produced by LLMs."""

from __future__ import annotations

import re

SQL_SELECT_PATTERN = re.compile(r"(?is)(SELECT\s.+)$")
SQL_LABEL_PATTERN = re.compile(r"^\s*sql\s*:\s*", flags=re.IGNORECASE)
THINK_PATTERN = re.compile(r"<think>.*?</think>", flags=re.IGNORECASE | re.DOTALL)
SQL_FENCE_PATTERN = re.compile(r"^\s*```sql\s*(.*?)\s*```\s*$", flags=re.IGNORECASE | re.DOTALL)
GENERIC_FENCE_PATTERN = re.compile(r"^\s*```\s*(.*?)\s*```\s*$", flags=re.DOTALL)


def strip_think_blocks(text: str) -> str:
    """Remove <think>...</think> scaffolding from LLM output."""
    return THINK_PATTERN.sub("", text).strip()


def strip_code_fences(text: str) -> str:
    """Remove markdown code fence wrappers, returning the enclosed snippet."""
    match = SQL_FENCE_PATTERN.match(text)
    if match:
        return match.group(1).strip()
    match = GENERIC_FENCE_PATTERN.match(text)
    if match:
        return match.group(1).strip()
    return text.replace("```", "").strip()


def trim_trailing_semicolons(sql: str) -> str:
    """Remove trailing semicolons to avoid multi-statement execution."""
    return re.sub(r";+\s*$", "", sql).strip()


def clean_sql_output(raw: str) -> str:
    """Normalise raw LLM output to a single SELECT statement."""
    sql = raw.strip()
    if not sql:
        return ""

    sql = strip_think_blocks(sql)
    sql = strip_code_fences(sql)
    sql = SQL_LABEL_PATTERN.sub("", sql)
    sql = sql.strip('"').strip("'")

    match = SQL_SELECT_PATTERN.search(sql)
    if match:
        sql = match.group(1)

    sql = sql.replace("`", "")
    sql = sql.replace("\n", " ")
    sql = re.sub(r"\s+", " ", sql)
    sql = trim_trailing_semicolons(sql)
    return sql.strip()
