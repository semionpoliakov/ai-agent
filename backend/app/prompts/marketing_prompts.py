from __future__ import annotations

import json
from typing import Any, Iterable

from app.services.clickhouse_schema import (
    COLUMNS,
    DERIVED_METRICS,
    TABLE_NAME,
    ColumnDefinition,
)

DEFAULT_ROW_LIMIT = 100


def _format_table(columns: Iterable[ColumnDefinition]) -> str:
    return "\n".join(f"- {column.name} {column.data_type}" for column in columns)


def _format_history(history: list[str]) -> str:
    if not history:
        return "No previous user questions."
    numbered = [f"{idx + 1}. {message}" for idx, message in enumerate(history)]
    return "\n".join(numbered)


def build_sql_prompt(question: str, history: list[str]) -> str:
    table_description = _format_table(COLUMNS)
    derived_description = "\n".join(f"- {name} = {expression}" for name, expression in DERIVED_METRICS.items())
    return f"""You are an expert marketing analytics engineer working with ClickHouse.
Use the available table `{TABLE_NAME}` with columns:
{table_description}

Derived metrics available for reporting:
{derived_description}

Conversation history:
{_format_history(history)}

Task:
Return a single ClickHouse SQL SELECT statement that answers the new question.
- Always aggregate data appropriately.
- Include sample usage of quantiles(0.25, 0.5, 0.75)(spend) and uniqExact(campaign_id) when summarising spend distribution or campaign variety.
- Never modify data (read-only).
- Provide well-aliased columns using snake_case.
- Limit rows to {DEFAULT_ROW_LIMIT} by default.
- Use date truncation when fetching multi-day ranges.

Return ONLY the SQL string with no explanation.

New question: {question}"""


def build_summary_prompt(question: str, sql: str, rows: list[dict[str, Any]]) -> str:
    dataset = json.dumps(rows, ensure_ascii=False)
    return f"""You are a marketing analyst.
You previously generated the following SQL query:
{sql}

It produced this JSON result set:
{dataset}

Write a concise answer for the business stakeholder.
- Explain the key findings in plain English.
- Highlight metrics such as spend, clicks, ctr, roas.
- Mention any notable quantiles or campaign counts if present.
- Keep the tone factual and actionable.

User question that triggered this analysis: {question}"""
