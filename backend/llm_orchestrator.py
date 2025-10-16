from __future__ import annotations

import json
import logging
import time
from hashlib import sha256
from typing import Any

from backend.app.core.cache import fingerprint as make_fingerprint
from backend.app.core.cache import read_cache, write_cache
from backend.app.core.context import get_memory
from backend.app.core.config import get_settings
from backend.app.services.clickhouse import get_clickhouse_client
from backend.app.services.llm_client import get_gemini_client
from backend.app.services.sql_validator import allow_only_select

logger = logging.getLogger(__name__)

SETTINGS = get_settings()
MEMORY = get_memory()


def _question_key(question: str) -> str:
    digest = sha256(question.strip().lower().encode("utf-8")).hexdigest()
    return f"cache:question:{digest}"


async def _lookup_cache(question: str) -> dict[str, Any] | None:
    question_key = _question_key(question)
    mapping = await read_cache(question_key)
    if not mapping:
        return None
    fingerprint_key = mapping.get("fingerprint")
    if not fingerprint_key:
        return None
    return await read_cache(fingerprint_key)


async def _store_cache(question: str, fingerprint_key: str, payload: dict[str, Any]) -> None:
    question_key = _question_key(question)
    await write_cache(fingerprint_key, payload)
    await write_cache(question_key, {"fingerprint": fingerprint_key})


def _format_history(history: list[str]) -> str:
    if not history:
        return "No previous user questions."
    numbered = [f"{idx + 1}. {message}" for idx, message in enumerate(history[-SETTINGS.max_history_messages :])]
    return "\n".join(numbered)


def _build_sql_prompt(question: str, history: list[str]) -> str:
    return f"""You are an expert marketing analytics engineer working with ClickHouse.\nUse the available table `ad_performance` with columns:\n- date Date\n- source String\n- campaign_id UInt32\n- campaign_name String\n- country String\n- impressions UInt32\n- clicks UInt32\n- spend Float32\n- conversions UInt32\n- revenue Float32\n\nDerived metrics available for reporting:\n- ctr = clicks / impressions\n- cpc = spend / clicks\n- roas = revenue / spend\n\nUser conversation history (latest first):\n{_format_history(history)}\n\nTask:\nReturn a single ClickHouse SQL SELECT statement that answers the new question.\n- Always aggregate data appropriately.\n- Include sample usage of quantiles(0.25, 0.5, 0.75)(spend) and uniqExact(campaign_id) when summarising spend distribution or unique campaigns.\n- Never modify data (read-only).\n- Provide well-aliased columns using snake_case.\n- Limit rows to 100 by default.\n- Use Date truncation when fetching multi-day ranges.\n\nReturn ONLY the SQL string with no explanation.\n\nNew question: {question}"""


def _build_summary_prompt(question: str, sql: str, rows: list[dict[str, Any]]) -> str:
    dataset = json.dumps(rows, ensure_ascii=False)
    return f"""You are a marketing analyst.\nYou previously generated the following SQL query:\n{sql}\n\nIt produced this JSON result set:\n{dataset}\n\nWrite a concise answer for the business stakeholder.\n- Explain the key findings in plain English.\n- Highlight metrics such as spend, clicks, ctr, roas.\n- Mention any notable quantiles or campaign counts if present.\n- Keep the tone factual and actionable.\n\nUser question that triggered this analysis: {question}"""


async def run_agent(question: str, user_id: str | None) -> dict[str, Any]:
    start_time = time.perf_counter()
    cached = await _lookup_cache(question)
    if cached:
        logger.info("cache_hit question=%s", question[:80])
        if user_id:
            MEMORY.add(user_id, f"Q: {question}")
            MEMORY.add(user_id, f"A: {cached['summary']}")
        return cached

    history = MEMORY.get_recent(user_id) if user_id else []
    memory_payload = history + [f"Q: {question}"]

    gemini = get_gemini_client()
    sql_prompt = _build_sql_prompt(question, memory_payload)
    sql_raw = await gemini.generate_text(sql_prompt)

    sql = allow_only_select(sql_raw)

    clickhouse = get_clickhouse_client()
    rows = await clickhouse.execute(sql)

    summary_prompt = _build_summary_prompt(question, sql, rows)
    summary = await gemini.generate_text(summary_prompt)

    if user_id:
        MEMORY.add(user_id, f"Q: {question}")
        MEMORY.add(user_id, f"A: {summary}")

    payload = {
        "sql": sql,
        "data": rows,
        "summary": summary,
    }

    fp = make_fingerprint(question, sql)
    fingerprint_key = f"cache:fingerprint:{fp}"
    await _store_cache(question, fingerprint_key, payload)

    elapsed = time.perf_counter() - start_time
    logger.info("query_latency_seconds=%.3f", elapsed)
    return payload
