from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .api.routes import limiter
from .api.routes import router as query_router
from .core.cache import get_redis
from .core.config import get_settings
from .models.schemas import HealthResponse
from .services.clickhouse import get_clickhouse_client

settings = get_settings()
logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.app_name)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

if settings.frontend_cors_origin:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(settings.frontend_cors_origin)],
        allow_credentials=True,
        allow_methods=["POST", "GET", "OPTIONS"],
        allow_headers=["*"],
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    clickhouse_ok = False
    redis_ok = False

    try:
        clickhouse = get_clickhouse_client()
        await clickhouse.execute("SELECT 1")
        clickhouse_ok = True
    except Exception:  # noqa: BLE001
        logging.exception("ClickHouse health check failed")

    try:
        redis = await get_redis()
        await redis.ping()
        redis_ok = True
    except Exception:  # noqa: BLE001
        logging.exception("Redis health check failed")

    status = "ok" if clickhouse_ok and redis_ok else "degraded"
    return HealthResponse(status=status, clickhouse=clickhouse_ok, redis=redis_ok)


app.include_router(query_router, prefix=settings.api_prefix)
