"""CORS configuration helpers."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings


def configure_cors(app: FastAPI, settings: Settings) -> None:
    if not settings.cors_allowed_origin:
        return
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.cors_allowed_origin],
        allow_credentials=False,
        allow_methods=["POST", "OPTIONS", "GET"],
        allow_headers=["*"],
    )
