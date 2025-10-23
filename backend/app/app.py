"""Application factory for the FastAPI service."""

from __future__ import annotations

import logging
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import Response

from .api.errors import register_exception_handlers
from .api.health import router as health_router
from .api.routes import limiter
from .api.routes import router as query_router
from .infra.clickhouse.bootstrap import bootstrap_clickhouse
from .infra.clickhouse.client import get_clickhouse_client
from .infra.config import Settings, get_settings
from .infra.cors import configure_cors
from .infra.logging import bind_request_id, clear_request_id, configure_logging

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(title=settings.app_name)
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

    @app.on_event("startup")
    async def _bootstrap() -> None:
        clickhouse = get_clickhouse_client()
        try:
            await bootstrap_clickhouse(clickhouse)
        except Exception:
            logger.exception("Failed to bootstrap ClickHouse dataset")

    app.include_router(health_router)
    app.include_router(query_router, prefix=settings.api_prefix)

    return app
