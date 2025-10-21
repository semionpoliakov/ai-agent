from __future__ import annotations

import re

_SQL_BLOCK_PATTERN = re.compile(r"```sql\s*(.*?)```", flags=re.IGNORECASE | re.DOTALL)
_GENERIC_BLOCK_PATTERN = re.compile(r"^```[a-zA-Z]*\n?|```$", flags=re.MULTILINE)
_THINK_TAG_PATTERN = re.compile(r"</?think>", flags=re.IGNORECASE)
_SELECT_PATTERN = re.compile(r"(?is)(SELECT\s.+)$")


def clean_sql_output(raw: str) -> str:
    """Normalize LLM output to a single SELECT statement free of markdown or stray quotes."""
    sql = raw.strip()
    if not sql:
        return ""

    blocks = _SQL_BLOCK_PATTERN.findall(sql)
    if blocks:
        sql = blocks[0]
    else:
        sql = _GENERIC_BLOCK_PATTERN.sub("", sql)

    sql = _THINK_TAG_PATTERN.sub("", sql)
    sql = sql.replace('\"', '"').replace("''", "'")
    sql = re.sub(r'["]+$', "", sql).strip()

    match = _SELECT_PATTERN.search(sql)
    if match:
        sql = match.group(1).strip()

    if sql.endswith('"') or sql.endswith("'"):
        sql = sql[:-1]

    return sql.strip()
