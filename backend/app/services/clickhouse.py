from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from clickhouse_driver import Client

from ..core.config import get_settings


@dataclass(slots=True)
class ClickHouseSettings:
    host: str
    port: int
    database: str


def _parse_clickhouse_url(url: str) -> ClickHouseSettings:
    parsed = urlparse(url)
    if parsed.scheme != "clickhouse":
        raise ValueError("CLICKHOUSE_URL must use clickhouse:// scheme")
    host = parsed.hostname or "localhost"
    port = parsed.port or 9000
    database = parsed.path.lstrip("/") or "default"
    return ClickHouseSettings(host=host, port=port, database=database)


class ClickHouseClient:
    def __init__(self) -> None:
        settings = get_settings()
        metadata = _parse_clickhouse_url(str(settings.clickhouse_url))
        self._client = Client(
            host=metadata.host,
            port=metadata.port,
            database=metadata.database,
            user=settings.clickhouse_user,
            password=settings.clickhouse_password.get_secret_value(),
        )

    async def execute(self, sql: str) -> list[dict[str, Any]]:
        loop = asyncio.get_running_loop()
        data, columns = await loop.run_in_executor(None, self._run_query, sql)
        column_names = [col[0] for col in columns]
        return [dict(zip(column_names, row)) for row in data]

    def _run_query(self, sql: str) -> tuple[list[Any], list[Any]]:
        return self._client.execute(sql, with_column_types=True)


_clickhouse_client: ClickHouseClient | None = None


def get_clickhouse_client() -> ClickHouseClient:
    global _clickhouse_client
    if _clickhouse_client is None:
        _clickhouse_client = ClickHouseClient()
    return _clickhouse_client
