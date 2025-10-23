"""Utilities to render prompt templates with runtime context."""

from __future__ import annotations

import json
from collections.abc import Iterable

from ...infra.clickhouse.schema import COLUMNS, DERIVED_METRICS, TABLE_NAME, ColumnDefinition
from ..prompts import load_prompt

DEFAULT_ROW_LIMIT = 100


def _format_table(columns: Iterable[ColumnDefinition]) -> str:
    return "\n".join(f"- {column.name} {column.data_type}" for column in columns)


def _format_history(history: list[str]) -> str:
    if not history:
        return "No previous user questions."
    numbered = [f"{idx + 1}. {message}" for idx, message in enumerate(history)]
    return "\n".join(numbered)


def render_sql_prompt(question: str, history: list[str]) -> str:
    template = load_prompt("sql_prompt")
    return template.format(
        table_name=TABLE_NAME,
        table_description=_format_table(COLUMNS),
        derived_description="\n".join(
            f"- {name} = {expression}" for name, expression in DERIVED_METRICS.items()
        ),
        conversation_history=_format_history(history),
        default_row_limit=DEFAULT_ROW_LIMIT,
        question=question,
    )


def render_summary_prompt(question: str, sql: str, rows: list[dict[str, object]]) -> str:
    template = load_prompt("summary_prompt")
    dataset = json.dumps(rows, ensure_ascii=False)
    return template.format(question=question, sql=sql, dataset=dataset)
