"""Root router for API endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from ...infra.config import get_settings
from ...infra.rate_limit import build_rate_limiter

settings = get_settings()
limiter = build_rate_limiter(settings)


def _build_router() -> APIRouter:
    router = APIRouter()
    from . import query  # noqa: E402  # isort: skip

    router.include_router(query.router, prefix="/query", tags=["query"])
    return router


router = _build_router()

__all__ = ["router", "limiter"]
