"""Canonical ClickHouse schema description used for bootstrapping and prompts."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, timedelta

TABLE_NAME = "ad_performance"


@dataclass(frozen=True, slots=True)
class ColumnDefinition:
    name: str
    data_type: str
    description: str


COLUMNS: Sequence[ColumnDefinition] = (
    ColumnDefinition("date", "Date", "Calendar date of the campaign performance"),
    ColumnDefinition("source", "String", "Acquisition channel such as facebook_ads or google_ads"),
    ColumnDefinition("campaign_id", "UInt32", "Internal numeric campaign identifier"),
    ColumnDefinition("campaign_name", "String", "Descriptive marketing campaign name"),
    ColumnDefinition("country", "String", "ISO country code for the traffic segment"),
    ColumnDefinition("impressions", "UInt32", "Number of times the ad was shown"),
    ColumnDefinition("clicks", "UInt32", "Number of clicks recorded"),
    ColumnDefinition("spend", "Float32", "Advertising spend in USD"),
    ColumnDefinition("conversions", "UInt32", "Number of desired conversion events"),
    ColumnDefinition("revenue", "Float32", "Attributed revenue in USD"),
)


DERIVED_METRICS: dict[str, str] = {
    "ctr": "clicks / impressions",
    "cpc": "spend / clicks",
    "roas": "revenue / spend",
}


def _iter_column_sql(columns: Iterable[ColumnDefinition] = COLUMNS) -> str:
    return ",\n    ".join(f"{col.name} {col.data_type}" for col in columns)


def build_create_table_statement(database: str | None = None) -> str:
    table_identifier = f"{database}.{TABLE_NAME}" if database else TABLE_NAME
    return f"""CREATE TABLE IF NOT EXISTS {table_identifier} (
    {_iter_column_sql()}
)
ENGINE = MergeTree()
ORDER BY (date, source, campaign_id)
PRIMARY KEY (date, source, campaign_id)
"""


CREATE_TABLE_STATEMENT = build_create_table_statement()


SeedRow = tuple[date, str, int, str, str, int, int, float, int, float]


def generate_seed_rows(days: int = 30) -> list[SeedRow]:
    """Generate deterministic seed data covering the most recent `days` window."""
    today = date.today()
    start = today - timedelta(days=days - 1)
    sources = ("facebook_ads", "google_ads")
    countries = ("US", "GB", "DE", "FR", "CA")

    rows: list[SeedRow] = []
    campaign_id = 10_000

    for offset in range(days):
        current = start + timedelta(days=offset)
        for source_index, source in enumerate(sources):
            campaign_id += 1
            impressions = 5_000 + (offset * 230) + source_index * 150
            clicks = max(1, int(impressions * (0.05 + source_index * 0.01)))
            spend = round(250 + offset * 12.5 + source_index * 20, 2)
            conversions = max(0, int(clicks * 0.08))
            revenue = round(spend * (1.8 + source_index * 0.4), 2)

            rows.append(
                (
                    current,
                    source,
                    campaign_id,
                    f"{source.replace('_', ' ').title()} Campaign {campaign_id}",
                    countries[(offset + source_index) % len(countries)],
                    impressions,
                    clicks,
                    float(spend),
                    conversions,
                    float(revenue),
                )
            )

    return rows
