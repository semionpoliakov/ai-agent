from __future__ import annotations

from typing import Any

import pytest
from app.api import deps
from app.app import create_app
from app.domain.models import QueryRequest
from app.domain.services.orchestrator import QueryOrchestrator
from app.infra.cache.client import RedisCache
from app.infra.config import Settings, get_settings
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
    async def query(self, sql: str) -> list[dict[str, Any]]:
        return [{"source": "facebook", "total_spend": 123.45}]

    async def execute_scalar(self, sql: str) -> int:
        return 1


class InMemoryCache(RedisCache):
    def __init__(self, settings: Settings) -> None:  # type: ignore[override]
        super().__init__(settings)
        self._store: dict[str, Any] = {}

    async def read(self, key: str) -> dict[str, Any] | None:
        value = self._store.get(key)
        if value is None:
            return None
        return value

    async def write(self, key: str, value: dict[str, Any], ttl_seconds: int | None = None) -> None:
        self._store[key] = value


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
    stub_cache = InMemoryCache(settings)

    orchestrator = QueryOrchestrator(
        settings=settings,
        llm_client=stub_llm,
        clickhouse=stub_clickhouse,  # type: ignore[arg-type]
        cache=stub_cache,
    )

    monkeypatch.setattr("app.app.get_clickhouse_client", lambda: stub_clickhouse)

    async def _bootstrap(_: object) -> dict[str, object]:
        return {"table": "stub", "created": False, "seeded": False, "row_count": 1}

    monkeypatch.setattr("app.app.bootstrap_clickhouse", _bootstrap)

    app = create_app(settings)

    app.dependency_overrides[deps.get_orchestrator_dep] = lambda: orchestrator
    app.dependency_overrides[deps.get_clickhouse_dep] = lambda: stub_clickhouse  # type: ignore[return-value]
    app.dependency_overrides[deps.get_cache_dep] = lambda: stub_cache

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
