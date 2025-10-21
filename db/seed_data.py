from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from clickhouse_driver import Client

import sys

ROOT = Path(__file__).resolve().parent.parent
BACKEND_PATH = ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.services.clickhouse_schema import TABLE_NAME, build_create_table_statement, generate_seed_rows  # noqa: E402


def parse_clickhouse_url(url: str) -> tuple[str, int, str]:
    parsed = urlparse(url)
    if parsed.scheme != "clickhouse":
        raise ValueError("CLICKHOUSE_URL must use clickhouse:// scheme")
    host = parsed.hostname or "localhost"
    port = parsed.port or 9000
    database = parsed.path.lstrip("/") or "marketing"
    return host, port, database


def main() -> None:
    clickhouse_url = os.environ.get("CLICKHOUSE_URL", "clickhouse://localhost:9000/marketing")
    user = os.environ.get("CLICKHOUSE_USER", "default")
    password = os.environ.get("CLICKHOUSE_PASSWORD", "")

    host, port, database = parse_clickhouse_url(clickhouse_url)

    client = Client(host=host, port=port, database=database, user=user, password=password)

    client.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    client.execute(build_create_table_statement(database))

    rows = generate_seed_rows(days=45)
    if not rows:
        raise RuntimeError("No rows generated for seed")

    client.execute(f"TRUNCATE TABLE {database}.{TABLE_NAME}")
    client.execute(
        f"INSERT INTO {database}.{TABLE_NAME} VALUES",
        rows,
        types_check=True,
    )

    print(f"Seeded {len(rows)} rows into {database}.{TABLE_NAME}")


if __name__ == "__main__":
    main()
