"""Utilities to populate ClickHouse with demonstration marketing data."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from clickhouse_driver import Client as SyncClickHouseClient

from .schema import TABLE_NAME, build_create_table_statement, generate_seed_rows

if TYPE_CHECKING:
    from .client import ClickHouseClient

logger = logging.getLogger(__name__)


def parse_clickhouse_url(url: str) -> tuple[str, int, str]:
    parsed = urlparse(url)
    if parsed.scheme != "clickhouse":
        raise ValueError("CLICKHOUSE_URL must use clickhouse:// scheme")
    host = parsed.hostname or "localhost"
    port = parsed.port or 9000
    database = parsed.path.lstrip("/") or "marketing"
    return host, port, database


def _seed_with_executor(
    execute: Callable[..., Any],
    *,
    database: str,
    days: int,
    sources: Sequence[str],
    create_database: bool,
) -> int:
    sources_tuple = tuple(sources)

    if create_database:
        execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    execute(build_create_table_statement(database))

    rows = generate_seed_rows(days=days, sources=sources_tuple)
    if not rows:
        raise RuntimeError("No rows generated for seed")

    execute(f"TRUNCATE TABLE {database}.{TABLE_NAME}")
    execute(
        f"INSERT INTO {database}.{TABLE_NAME} VALUES",
        rows,
        types_check=True,
    )

    logger.info(
        "clickhouse_seed_completed rows=%d database=%s table=%s sources=%s",
        len(rows),
        database,
        TABLE_NAME,
        ", ".join(sources_tuple),
    )
    return len(rows)


def seed_clickhouse_with_client(
    client: "ClickHouseClient",
    *,
    days: int = 45,
    sources: Sequence[str] = ("google", "facebook"),
) -> int:
    return _seed_with_executor(
        client.execute_sync,
        database=client.database,
        days=days,
        sources=sources,
        create_database=False,
    )


def seed_clickhouse(
    *,
    clickhouse_url: str,
    user: str,
    password: str,
    days: int = 45,
    sources: Sequence[str] = ("google", "facebook"),
) -> int:
    host, port, database = parse_clickhouse_url(clickhouse_url)
    client = SyncClickHouseClient(host=host, port=port, database=database, user=user, password=password)
    return _seed_with_executor(
        client.execute,
        database=database,
        days=days,
        sources=sources,
        create_database=True,
    )


def main() -> None:
    clickhouse_url = os.environ.get("CLICKHOUSE_URL", "clickhouse://localhost:9000/marketing")
    user = os.environ.get("CLICKHOUSE_USER", "default")
    password = os.environ.get("CLICKHOUSE_PASSWORD", "")

    seed_clickhouse(clickhouse_url=clickhouse_url, user=user, password=password)


if __name__ == "__main__":
    main()
