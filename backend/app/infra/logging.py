"""Logging utilities for consistent, structured application logs."""

from __future__ import annotations

import logging
import os
import sys
import uuid
from contextvars import ContextVar

from .config import Settings

_REQUEST_ID: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Inject the active request id into log records."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        record.request_id = _REQUEST_ID.get("-")
        return True


def configure_logging(settings: Settings) -> None:
    """Configure application-wide logging sinks."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = logging.getLevelName(level_name)
    formatter = logging.Formatter(
        fmt=(
            "time=%(asctime)s level=%(levelname)s name=%(name)s "
            "request_id=%(request_id)s message=%(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers = [handler]
    root.addFilter(RequestIdFilter())

    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []
    logging.getLogger("uvicorn").propagate = False

    logging.getLogger(__name__).info("logging_configured %s", settings.sanitized_config)


def bind_request_id() -> str:
    """Generate and bind a fresh request id for the active context."""
    request_id = uuid.uuid4().hex
    _REQUEST_ID.set(request_id)
    return request_id


def clear_request_id() -> None:
    """Clear any request id bound to the current context."""
    _REQUEST_ID.set("-")
