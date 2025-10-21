from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from clickhouse_driver import Client

from ..core.config import get_settings
from .clickhouse_schema import TABLE_NAME, build_create_table_statement, generate_seed_rows

logger = logging.getLogger(__name__)


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
        self._database = metadata.database
        self._client = Client(
            host=metadata.host,
            port=metadata.port,
            database=metadata.database,
            user=settings.clickhouse_user,
            password=settings.clickhouse_password.get_secret_value(),
        )
        self._table_identifier = f"{self._database}.{TABLE_NAME}" if self._database else TABLE_NAME
        logger.info(
            "clickhouse_client_connected host=%s port=%s database=%s",
            metadata.host,
            metadata.port,
            self._database,
        )

    async def execute(self, sql: str) -> list[dict[str, Any]]:
        loop = asyncio.get_running_loop()
        data, columns = await loop.run_in_executor(None, self._run_query, sql)
        column_names = [col[0] for col in columns]
        return [dict(zip(column_names, row, strict=False)) for row in data]

    def _run_query(self, sql: str) -> tuple[list[Any], list[Any]]:
        return self._client.execute(sql, with_column_types=True)

    async def ensure_table_seeded(self) -> dict[str, Any]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._ensure_table_seeded_sync)

    def _ensure_table_seeded_sync(self) -> dict[str, Any]:
        summary = {
            "table": self._table_identifier,
            "created": False,
            "seeded": False,
            "row_count": 0,
        }

        create_statement = build_create_table_statement(self._database) if self._database else build_create_table_statement()
        exists_query = f"EXISTS TABLE {self._table_identifier}"

        exists_result = self._client.execute(exists_query)
        exists = bool(exists_result and exists_result[0][0])

        if not exists:
            self._client.execute(create_statement)
            summary["created"] = True

        count_query = f"SELECT count() FROM {self._table_identifier}"
        count_result = self._client.execute(count_query)
        row_count = int(count_result[0][0]) if count_result else 0
        summary["row_count"] = row_count

        if row_count == 0:
            rows = generate_seed_rows(days=30)
            if rows:
                self._client.execute(
                    f"INSERT INTO {self._table_identifier} VALUES",
                    rows,
                    types_check=True,
                )
                summary["seeded"] = True
                count_result = self._client.execute(count_query)
                summary["row_count"] = int(count_result[0][0]) if count_result else len(rows)

        return summary


_clickhouse_client: ClickHouseClient | None = None


def get_clickhouse_client() -> ClickHouseClient:
    global _clickhouse_client
    if _clickhouse_client is None:
        _clickhouse_client = ClickHouseClient()
    return _clickhouse_client
