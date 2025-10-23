"""Runtime configuration primitives loaded from environment variables.

This module centralises environment parsing so that the rest of the application
can rely on a single `Settings` instance with well-typed attributes. The
settings schema mirrors operational knobs that operators are expected to tune
when deploying the service. Use `get_settings()` to obtain a cached instance.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Self

from dotenv import load_dotenv
from pydantic import AnyUrl, Field, PositiveInt, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class ClickHouseUrl(AnyUrl):
    allowed_schemes = {"clickhouse"}


class RedisUrl(AnyUrl):
    allowed_schemes = {"redis"}


class Settings(BaseSettings):
    """Strongly typed configuration surface for the application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="marketing-analytics-agent", alias="APP_NAME")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    clickhouse_url: ClickHouseUrl = Field(..., alias="CLICKHOUSE_URL")
    clickhouse_user: str = Field(..., alias="CLICKHOUSE_USER")
    clickhouse_password: SecretStr = Field(..., alias="CLICKHOUSE_PASSWORD")

    redis_url: RedisUrl = Field(..., alias="REDIS_URL")

    llm_provider: str = Field(default="groq", alias="LLM_PROVIDER")
    llm_model: str = Field(default="qwen/qwen3-32b", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE", ge=0.0, le=2.0)
    llm_api_key: SecretStr | None = Field(default=None, alias="LLM_API_KEY")
    groq_api_key: SecretStr | None = Field(default=None, alias="GROQ_API_KEY")

    max_history_messages: PositiveInt = Field(default=3, alias="MAX_HISTORY_MESSAGES")
    cache_ttl_seconds: PositiveInt = Field(default=3600, alias="CACHE_TTL_SECONDS")
    rate_limit_per_minute: PositiveInt = Field(default=30, alias="RATE_LIMIT_PER_MINUTE")
    cors_allowed_origin: str | None = Field(default=None, alias="CORS_ALLOWED_ORIGIN")

    @model_validator(mode="after")
    def _ensure_llm_configuration(self) -> Self:
        provider = (self.llm_provider or "").strip().lower()
        if provider == "groq":
            if self.llm_api_key is None and self.groq_api_key is not None:
                object.__setattr__(self, "llm_api_key", self.groq_api_key)
            if self.llm_api_key is None:
                raise ValueError("LLM_API_KEY is required when LLM_PROVIDER='groq'")
        elif provider in {"openai", "vertex"}:
            if self.llm_api_key is None:
                raise ValueError(f"LLM_API_KEY is required when LLM_PROVIDER='{provider}'")
        else:
            raise ValueError(f"Unsupported LLM provider '{self.llm_provider}'")
        return self

    @property
    def sanitized_config(self) -> dict[str, Any]:
        """Key-value mapping suitable for logging without leaking secrets."""
        return {
            "app_name": self.app_name,
            "api_prefix": self.api_prefix,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "max_history_messages": self.max_history_messages,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "cors_allowed_origin": self.cors_allowed_origin or "disabled",
            "clickhouse_url": str(self.clickhouse_url),
            "redis_url": str(self.redis_url),
        }


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide cached settings instance."""
    return Settings()  # type: ignore[call-arg]
