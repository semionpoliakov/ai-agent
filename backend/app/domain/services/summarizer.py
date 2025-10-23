"""LLM-backed summarisation for ClickHouse query results."""

from __future__ import annotations

from ...infra.llm.base import LLMClientProtocol
from .prompt_builder import render_summary_prompt
from .sql_builder import strip_think_blocks


class Summarizer:
    """Generate natural language summaries for query results."""

    def __init__(self, llm_client: LLMClientProtocol) -> None:
        self._llm = llm_client

    async def summarise(self, question: str, sql: str, rows: list[dict[str, object]]) -> str:
        prompt = render_summary_prompt(question, sql, rows)
        raw = await self._llm.generate_text(prompt)
        return strip_think_blocks(raw)
