from __future__ import annotations

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import AnyUrl, Field, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class ClickHouseUrl(AnyUrl):
    allowed_schemes = {"clickhouse"}


class RedisUrl(AnyUrl):
    allowed_schemes = {"redis"}


class Settings(BaseSettings):
    app_name: str = Field("marketing-analytics-agent", alias="APP_NAME")
    api_prefix: str = Field("/api/v1", alias="API_PREFIX")
    clickhouse_url: ClickHouseUrl = Field(..., alias="CLICKHOUSE_URL")
    clickhouse_user: str = Field(..., alias="CLICKHOUSE_USER")
    clickhouse_password: SecretStr = Field(..., alias="CLICKHOUSE_PASSWORD")
    redis_url: RedisUrl = Field(..., alias="REDIS_URL")
    gemini_api_key: SecretStr = Field(..., alias="GEMINI_API_KEY")
    gemini_model: str = Field("models/gemini-1.5-flash-latest", alias="GEMINI_MODEL")
    max_history_messages: PositiveInt = Field(3, alias="MAX_HISTORY_MESSAGES")
    cache_ttl_seconds: PositiveInt = Field(3600, alias="CACHE_TTL_SECONDS")
    rate_limit_per_minute: PositiveInt = Field(30, alias="RATE_LIMIT_PER_MINUTE")
    cors_allowed_origin: str | None = Field(None, alias="CORS_ALLOWED_ORIGIN")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
