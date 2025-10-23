"""Helpers to provision and seed ClickHouse tables."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from typing import Any

from .client import ClickHouseClient
from .schema import TABLE_NAME, build_create_table_statement
from .seed_data import main as seed_clickhouse_cli, seed_clickhouse_with_client

logger = logging.getLogger(__name__)


async def bootstrap_clickhouse(client: ClickHouseClient) -> dict[str, Any]:
    """Ensure the analytics table exists and seeded with demo data."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _bootstrap_sync, client)


def _bootstrap_sync(client: ClickHouseClient) -> dict[str, Any]:
    table_identifier = f"{client.database}.{TABLE_NAME}"
    summary = {"table": table_identifier, "created": False, "seeded": False, "row_count": 0}

    exists_query = f"EXISTS TABLE {table_identifier}"
    exists_result = client.execute_sync(exists_query)
    exists = bool(exists_result and exists_result[0][0])

    if not exists:
        create_statement = build_create_table_statement(client.database)
        client.execute_sync(create_statement)
        summary["created"] = True

    count_query = f"SELECT count() FROM {table_identifier}"
    count_result = client.execute_sync(count_query)
    row_count = int(count_result[0][0]) if count_result else 0
    summary["row_count"] = row_count

    if row_count == 0:
        inserted = seed_clickhouse_data(client, days=30, sources=["google", "facebook"])
        if inserted:
            summary["seeded"] = True
            count_result = client.execute_sync(count_query)
            summary["row_count"] = int(count_result[0][0]) if count_result else inserted

    logger.info(
        "clickhouse_bootstrap table=%s created=%s seeded=%s row_count=%s",
        summary["table"],
        summary["created"],
        summary["seeded"],
        summary["row_count"],
    )
    return summary


def seed_clickhouse_data(
    client: ClickHouseClient,
    *,
    days: int = 30,
    sources: Sequence[str] | None = None,
) -> int:
    active_sources = list(sources or ["google", "facebook"])
    return seed_clickhouse_with_client(
        client,
        days=days,
        sources=tuple(active_sources),
    )


def bootstrap_seed_clickhouse() -> None:
    seed_clickhouse_cli()
