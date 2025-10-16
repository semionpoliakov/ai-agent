from __future__ import annotations

import os
import random
from datetime import date, timedelta
from typing import Iterable
from urllib.parse import urlparse

from clickhouse_driver import Client
from faker import Faker

faker = Faker()


def parse_clickhouse_url(url: str) -> tuple[str, int, str]:
    parsed = urlparse(url)
    if parsed.scheme != "clickhouse":
        raise ValueError("CLICKHOUSE_URL must use clickhouse:// scheme")
    host = parsed.hostname or "localhost"
    port = parsed.port or 9000
    database = parsed.path.lstrip("/") or "marketing"
    return host, port, database


def generate_rows(days: int = 180) -> Iterable[tuple]:
    start = date.today() - timedelta(days=days)
    sources = ["facebook_ads", "google_ads"]
    countries = ["US", "GB", "DE", "FR", "CA", "AU"]

    rows: list[tuple] = []
    campaign_counter = 1

    for offset in range(days):
        current = start + timedelta(days=offset)
        for source in sources:
            for _ in range(random.randint(3, 6)):
                campaign_id = campaign_counter
                campaign_counter += 1
                impressions = random.randint(1_000, 80_000)
                ctr = random.uniform(0.01, 0.18)
                clicks = max(1, int(impressions * ctr))
                spend = round(random.uniform(80, 12_000), 2)
                conversions = max(0, int(clicks * random.uniform(0.02, 0.18)))
                roas_multiplier = random.uniform(0.8, 4.0)
                revenue = round(spend * roas_multiplier, 2)

                rows.append(
                    (
                        current,
                        source,
                        campaign_id,
                        faker.catch_phrase(),
                        random.choice(countries),
                        impressions,
                        clicks,
                        float(spend),
                        conversions,
                        float(revenue),
                    )
                )
    return rows


def main() -> None:
    clickhouse_url = os.environ.get("CLICKHOUSE_URL", "clickhouse://localhost:9000/marketing")
    user = os.environ.get("CLICKHOUSE_USER", "default")
    password = os.environ.get("CLICKHOUSE_PASSWORD", "")

    host, port, database = parse_clickhouse_url(clickhouse_url)

    client = Client(host=host, port=port, database=database, user=user, password=password)

    client.execute("CREATE DATABASE IF NOT EXISTS marketing")
    client.execute(
        """
        CREATE TABLE IF NOT EXISTS marketing.ad_performance (
            date Date,
            source String,
            campaign_id UInt32,
            campaign_name String,
            country String,
            impressions UInt32,
            clicks UInt32,
            spend Float32,
            conversions UInt32,
            revenue Float32
        )
        ENGINE = MergeTree()
        ORDER BY (date, source)
        """
    )

    rows = list(generate_rows())
    if not rows:
        raise RuntimeError("No rows generated for seed")

    client.execute("TRUNCATE TABLE marketing.ad_performance")
    client.execute(
        "INSERT INTO marketing.ad_performance VALUES",
        rows,
        types_check=True,
    )

    print(f"Seeded {len(rows)} marketing performance rows")


if __name__ == "__main__":
    main()
