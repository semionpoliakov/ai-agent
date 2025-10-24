"""Application factory for the FastAPI service."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from redis.asyncio import Redis
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import Response

from .api.errors import register_exception_handlers
from .api.health import router as health_router
from .api.routes import limiter
from .api.routes import router as query_router
from .domain.services.orchestrator import QueryOrchestrator
from .infra.cache.client import RedisCache
from .infra.clickhouse.bootstrap import bootstrap_clickhouse
from .infra.clickhouse.client import ClickHouseClient
from .infra.config import Settings, get_settings
from .infra.cors import configure_cors
from .infra.llm.factory import get_llm_client
from .infra.logging import bind_request_id, clear_request_id, configure_logging

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("application_startup_begin")

        clickhouse_client = ClickHouseClient(settings)
        redis_client = Redis.from_url(
            str(settings.redis_url),
            encoding="utf-8",
            decode_responses=True,
        )
        cache = RedisCache(redis_client, settings)
        llm_client = get_llm_client(settings)
        orchestrator = QueryOrchestrator(
            settings=settings,
            llm_client=llm_client,
            clickhouse=clickhouse_client,
            cache=cache,
        )

        app.state.settings = settings
        app.state.clickhouse_client = clickhouse_client
        app.state.redis_client = redis_client
        app.state.cache = cache
        app.state.llm_client = llm_client
        app.state.orchestrator = orchestrator

        try:
            await bootstrap_clickhouse(clickhouse_client)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to bootstrap ClickHouse dataset")

        logger.info("application_startup_complete")
        try:
            yield
        finally:
            logger.info("application_shutdown_begin")
            try:
                await redis_client.close()
            except Exception:  # noqa: BLE001
                logger.exception("Error while closing Redis client")
            try:
                await clickhouse_client.close()
            except Exception:  # noqa: BLE001
                logger.exception("Error while closing ClickHouse client")
            logger.info("application_shutdown_complete")

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    configure_cors(app, settings)
    register_exception_handlers(app)

    @app.middleware("http")
    async def request_id_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = bind_request_id()
        try:
            response = await call_next(request)
        finally:
            clear_request_id()
        response.headers["X-Request-ID"] = request_id
        return response

    app.include_router(health_router)
    app.include_router(query_router, prefix=settings.api_prefix)

    return app
