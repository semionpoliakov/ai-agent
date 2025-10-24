from __future__ import annotations

from typing import Any

import pytest
from app.app import create_app
from app.domain.models import QueryRequest
from app.domain.services.orchestrator import QueryOrchestrator
from app.infra.cache.client import RedisCache
from app.infra.config import get_settings
from app.infra.llm.base import LLMClientProtocol
from fastapi.testclient import TestClient


class StubLLM(LLMClientProtocol):
    def __init__(self) -> None:
        self._last_prompt: str | None = None

    async def generate_text(self, prompt: str, *, temperature: float | None = None) -> str:
        self._last_prompt = prompt
        if "JSON result" in prompt:
            return "The results look great."
        return "SELECT source, sum(spend) AS total_spend FROM ad_performance LIMIT 10"


class StubClickHouse:
    def __init__(self) -> None:
        self.database = "default"

    async def query(self, sql: str) -> list[dict[str, Any]]:
        return [{"source": "facebook", "total_spend": 123.45}]

    async def execute_scalar(self, sql: str) -> int:
        return 1

    def execute_sync(self, sql: str, *args: Any, **kwargs: Any) -> list[tuple[int]]:
        return [(1,)]

    async def close(self) -> None:
        return None


class StubRedis:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._store[key] = value

    async def ping(self) -> bool:
        return True

    async def close(self) -> None:
        return None


@pytest.fixture(autouse=True)
def configure_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLICKHOUSE_URL", "clickhouse://localhost:9000/default")
    monkeypatch.setenv("CLICKHOUSE_USER", "default")
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "password")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_API_KEY", "stub-key")
    monkeypatch.setenv("APP_NAME", "test-app")
    monkeypatch.setenv("API_PREFIX", "/api/v1")
    monkeypatch.setenv("CACHE_TTL_SECONDS", "60")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "100")
    get_settings.cache_clear()  # type: ignore[attr-defined]


def test_query_endpoint_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    QueryRequest.model_rebuild()
    settings = get_settings()
    stub_llm = StubLLM()
    stub_clickhouse = StubClickHouse()
    stub_redis = StubRedis()
    stub_cache = RedisCache(stub_redis, settings)

    orchestrator = QueryOrchestrator(
        settings=settings,
        llm_client=stub_llm,
        clickhouse=stub_clickhouse,  # type: ignore[arg-type]
        cache=stub_cache,
    )

    monkeypatch.setattr("app.app.ClickHouseClient", lambda *_args, **_kwargs: stub_clickhouse)

    async def _bootstrap(_: object) -> dict[str, object]:
        return {"table": "stub", "created": False, "seeded": False, "row_count": 1}

    monkeypatch.setattr("app.app.bootstrap_clickhouse", _bootstrap)
    monkeypatch.setattr("app.app.Redis.from_url", lambda *args, **kwargs: stub_redis)
    monkeypatch.setattr("app.app.RedisCache", lambda redis, settings: stub_cache)
    monkeypatch.setattr("app.app.get_llm_client", lambda _settings: stub_llm)
    monkeypatch.setattr("app.app.QueryOrchestrator", lambda **kwargs: orchestrator)

    app = create_app(settings)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/query",
            json={"question": "What is total spend by source?", "user_id": "user-123"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["sql"].startswith("SELECT")
        assert payload["data"] == [{"source": "facebook", "total_spend": 123.45}]
        assert "results look great" in payload["summary"].lower()
