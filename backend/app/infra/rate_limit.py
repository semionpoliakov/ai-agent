"""SlowAPI rate limiter configuration."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import Settings


def build_rate_limiter(settings: Settings) -> Limiter:
    """Create a rate limiter constrained by the configured requests per minute."""
    limit = f"{settings.rate_limit_per_minute}/minute"
    return Limiter(key_func=get_remote_address, default_limits=[limit])
