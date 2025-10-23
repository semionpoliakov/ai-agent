"""JSON serialization helpers tolerant of datetime objects."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any


def _default(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def to_json(obj: Any, *, ensure_ascii: bool = False) -> str:
    """Serialize an object to JSON with ISO handling for date/datetime."""
    return json.dumps(obj, ensure_ascii=ensure_ascii, default=_default)
