from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import AnyHttpUrl, BaseSettings, Field, PositiveInt, SecretStr, validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    app_name: str = Field("marketing-analytics-agent", alias="APP_NAME")
    api_prefix: str = Field("/api/v1", alias="API_PREFIX")
    clickhouse_url: AnyHttpUrl = Field(..., alias="CLICKHOUSE_URL")
    clickhouse_user: str = Field(..., alias="CLICKHOUSE_USER")
    clickhouse_password: SecretStr = Field(..., alias="CLICKHOUSE_PASSWORD")
    redis_url: AnyHttpUrl = Field(..., alias="REDIS_URL")
    gemini_api_key: SecretStr = Field(..., alias="GEMINI_API_KEY")
    gemini_model: str = Field("models/gemini-1.5-flash-latest", alias="GEMINI_MODEL")
    max_history_messages: PositiveInt = Field(3, alias="MAX_HISTORY_MESSAGES")
    cache_ttl_seconds: PositiveInt = Field(3600, alias="CACHE_TTL_SECONDS")
    rate_limit_per_minute: PositiveInt = Field(30, alias="RATE_LIMIT_PER_MINUTE")
    frontend_cors_origin: AnyHttpUrl | None = Field(None, alias="FRONTEND_CORS_ORIGIN")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("frontend_cors_origin", pre=True)
    def _empty_string_to_none(cls, value: Any) -> Any:
        if isinstance(value, str) and not value:
            return None
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
