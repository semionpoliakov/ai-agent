"""FastAPI dependency wiring for infrastructure components."""

from __future__ import annotations

from fastapi import Depends

from ..domain.services.orchestrator import QueryOrchestrator, get_orchestrator
from ..infra.cache.client import RedisCache, get_cache
from ..infra.clickhouse.client import ClickHouseClient, get_clickhouse_client
from ..infra.config import Settings, get_settings


def get_settings_dep() -> Settings:
    return get_settings()


def get_clickhouse_dep(settings: Settings = Depends(get_settings_dep)) -> ClickHouseClient:
    # Settings dependency ensures the instance is initialised before use.
    _ = settings
    return get_clickhouse_client()


def get_cache_dep(settings: Settings = Depends(get_settings_dep)) -> RedisCache:
    _ = settings
    return get_cache()


def get_orchestrator_dep(settings: Settings = Depends(get_settings_dep)) -> QueryOrchestrator:
    _ = settings
    return get_orchestrator()
