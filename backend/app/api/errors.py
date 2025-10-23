from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from ..infra.llm.factory import ProviderNotConfiguredError
from ..infra.logging import get_request_id

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    def _error_payload(detail: str) -> dict[str, str]:
        return {"detail": detail, "request_id": get_request_id() or "unknown"}

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=_error_payload("Too many requests"),
        )

    @app.exception_handler(ProviderNotConfiguredError)
    async def _provider_handler(request: Request, exc: ProviderNotConfiguredError) -> JSONResponse:
        logger.exception("LLM provider misconfigured: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload("LLM provider is not configured"),
        )

    @app.exception_handler(ValueError)
    async def _value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error_payload(str(exc)),
        )
