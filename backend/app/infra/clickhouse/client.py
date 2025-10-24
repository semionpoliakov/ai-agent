"""Async-friendly ClickHouse adapter built on top of clickhouse-driver."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, cast
from urllib.parse import urlparse

from clickhouse_driver import Client as SyncClickHouseClient  # type: ignore[import-untyped]

from ..config import Settings, get_settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ClickHouseConnectionSettings:
    host: str
    port: int
    database: str


def _parse_clickhouse_url(url: str) -> ClickHouseConnectionSettings:
    parsed = urlparse(url)
    if parsed.scheme != "clickhouse":
        raise ValueError("CLICKHOUSE_URL must use the clickhouse:// scheme")
    host = parsed.hostname or "localhost"
    port = parsed.port or 9000
    database = parsed.path.lstrip("/") or "default"
    return ClickHouseConnectionSettings(host=host, port=port, database=database)


class ClickHouseClient:
    """Thin asynchronous wrapper around the synchronous clickhouse-driver client."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._connection = _parse_clickhouse_url(str(self._settings.clickhouse_url))
        self._sync_client = SyncClickHouseClient(
            host=self._connection.host,
            port=self._connection.port,
            database=self._connection.database,
            user=self._settings.clickhouse_user,
            password=self._settings.clickhouse_password.get_secret_value(),
        )
        logger.info(
            "clickhouse_client_connected host=%s port=%s database=%s",
            self._connection.host,
            self._connection.port,
            self._connection.database,
        )

    @property
    def database(self) -> str:
        return self._connection.database

    async def query(self, sql: str) -> list[dict[str, Any]]:
        """Execute a read-only SQL statement and return rows as dicts."""
        loop = asyncio.get_running_loop()
        data, columns = await loop.run_in_executor(None, self._run_query, sql)
        column_names = [col[0] for col in columns]
        return [dict(zip(column_names, row, strict=False)) for row in data]

    async def execute_scalar(self, sql: str) -> Any:
        """Execute a query that returns a single scalar value."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self._sync_client.execute, sql)
        if not result:
            return None
        value = result[0]
        if isinstance(value, (list, tuple)):
            return value[0] if value else None
        return value

    def execute_sync(self, sql: str, *args: Any, **kwargs: Any) -> Any:
        """Run a synchronous statement directly. Primarily for bootstrap paths."""
        return self._sync_client.execute(sql, *args, **kwargs)

    def _run_query(self, sql: str) -> tuple[list[Any], list[Any]]:
        result = self._sync_client.execute(sql, with_column_types=True)
        return cast(tuple[list[Any], list[Any]], result)

    async def close(self) -> None:
        """Disconnect the underlying synchronous driver."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._sync_client.disconnect)
        logger.info("clickhouse_client_disconnected host=%s database=%s", self._connection.host, self._connection.database)
