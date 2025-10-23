"""Pydantic DTOs exposed by public HTTP APIs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Incoming request payload for the /query endpoint."""

    question: str = Field(..., min_length=3)
    user_id: str | None = Field(default=None, max_length=128)


class QueryResponse(BaseModel):
    """Response payload containing generated SQL, result rows, and summary."""

    sql: str
    data: list[dict[str, Any]]
    summary: str


class HealthResponse(BaseModel):
    """Health status response."""

    status: str
    clickhouse: bool
    redis: bool


QueryRequest.model_rebuild()
QueryResponse.model_rebuild()
HealthResponse.model_rebuild()
