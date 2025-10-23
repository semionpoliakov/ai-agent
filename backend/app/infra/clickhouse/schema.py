"""Canonical ClickHouse schema description used for bootstrapping and prompts."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from random import Random

TABLE_NAME = "ad_performance"


@dataclass(frozen=True, slots=True)
class ColumnDefinition:
    name: str
    data_type: str
    description: str


COLUMNS: Sequence[ColumnDefinition] = (
    ColumnDefinition("date", "Date", "Calendar date of the campaign performance"),
    ColumnDefinition("source", "String", "Acquisition channel such as facebook or google"),
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
ORDER BY (source, date, campaign_id)
PRIMARY KEY (source, date, campaign_id)
"""


CREATE_TABLE_STATEMENT = build_create_table_statement()


SeedRow = tuple[date, str, int, str, str, int, int, float, int, float]


def generate_seed_rows(
    days: int = 30,
    *,
    sources: Sequence[str] = ("google", "facebook"),
) -> list[SeedRow]:
    """Generate deterministic seed data covering the most recent window for given sources."""
    today = date.today()
    start = today - timedelta(days=days - 1)
    countries = ("US", "GB", "DE", "FR", "CA")
    rng = Random(42)

    profiles: dict[str, dict[str, tuple[float, float]]] = {
        "google": {
            "impressions": (1200, 4200),
            "ctr": (0.045, 0.08),
            "cpc": (0.9, 1.4),
            "conversion_rate": (0.025, 0.05),
            "roas": (1.85, 2.2),
        },
        "facebook": {
            "impressions": (2800, 6400),
            "ctr": (0.022, 0.05),
            "cpc": (0.55, 0.9),
            "conversion_rate": (0.02, 0.045),
            "roas": (1.65, 2.05),
        },
    }

    default_profile = {
        "impressions": (1500, 4500),
        "ctr": (0.03, 0.06),
        "cpc": (0.6, 1.0),
        "conversion_rate": (0.02, 0.05),
        "roas": (1.6, 2.1),
    }

    rows: list[SeedRow] = []
    campaign_id = 10_000

    for offset in range(days):
        current = start + timedelta(days=offset)
        for source in sources:
            profile = profiles.get(source, default_profile)
            impressions = rng.randint(int(profile["impressions"][0]), int(profile["impressions"][1]))
            ctr = rng.uniform(profile["ctr"][0], profile["ctr"][1])
            clicks = max(1, int(impressions * ctr))
            cpc = rng.uniform(profile["cpc"][0], profile["cpc"][1])
            spend = round(clicks * cpc, 2)
            conversion_rate = rng.uniform(profile["conversion_rate"][0], profile["conversion_rate"][1])
            conversions = min(clicks, int(clicks * conversion_rate))
            roas_multiplier = rng.uniform(profile["roas"][0], profile["roas"][1])
            revenue = round(spend * roas_multiplier, 2)
            campaign_id += 1
            rows.append(
                (
                    current,
                    source,
                    campaign_id,
                    f"{source.title()} Campaign {campaign_id}",
                    countries[(offset + rng.randint(0, len(countries) - 1)) % len(countries)],
                    impressions,
                    clicks,
                    float(spend),
                    conversions,
                    float(revenue),
                )
            )

    return rows
