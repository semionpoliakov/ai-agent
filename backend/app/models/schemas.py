from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3)
    user_id: str | None = Field(default=None, max_length=128)


class QueryResponse(BaseModel):
    sql: str
    data: list[dict[str, Any]]
    summary: str


class HealthResponse(BaseModel):
    status: str
    clickhouse: bool
    redis: bool
