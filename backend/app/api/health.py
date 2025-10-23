"""Health and readiness endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ..api.deps import get_cache_dep, get_clickhouse_dep
from ..domain.models import HealthResponse
from ..infra.cache.client import RedisCache, get_redis
from ..infra.clickhouse.client import ClickHouseClient

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    clickhouse: ClickHouseClient = Depends(get_clickhouse_dep),
    cache: RedisCache = Depends(get_cache_dep),
) -> HealthResponse:
    clickhouse_ok = False
    redis_ok = False

    try:
        await clickhouse.execute_scalar("SELECT 1")
        clickhouse_ok = True
    except Exception:  # noqa: BLE001
        logger.exception("ClickHouse health check failed")

    try:
        redis = await get_redis()
        await redis.ping()
        redis_ok = True
    except Exception:  # noqa: BLE001
        logger.exception("Redis health check failed")

    status = "ok" if clickhouse_ok and redis_ok else "degraded"
    return HealthResponse(status=status, clickhouse=clickhouse_ok, redis=redis_ok)


@router.get("/ready", response_model=HealthResponse)
async def ready_check(
    clickhouse: ClickHouseClient = Depends(get_clickhouse_dep),
    cache: RedisCache = Depends(get_cache_dep),
) -> HealthResponse:
    health = await health_check(clickhouse=clickhouse, cache=cache)
    if health.status != "ok":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": health.status,
                "clickhouse": health.clickhouse,
                "redis": health.redis,
            },
        )
    return health
