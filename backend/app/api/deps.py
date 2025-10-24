"""FastAPI dependency wiring for infrastructure components."""

from __future__ import annotations

from typing import cast

from fastapi import Depends, Request

from ..domain.services.orchestrator import QueryOrchestrator
from ..infra.cache.client import RedisCache
from ..infra.clickhouse.client import ClickHouseClient
from ..infra.config import Settings, get_settings


def get_settings_dep() -> Settings:
    return get_settings()


def get_clickhouse_dep(request: Request) -> ClickHouseClient:
    return cast(ClickHouseClient, request.app.state.clickhouse_client)


def get_cache_dep(request: Request) -> RedisCache:
    return cast(RedisCache, request.app.state.cache)


def get_orchestrator_dep(request: Request) -> QueryOrchestrator:
    return cast(QueryOrchestrator, request.app.state.orchestrator)
