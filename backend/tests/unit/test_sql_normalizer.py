from __future__ import annotations

import pytest

from app.infra.sql.normalizer import SQLNormalizationError, normalize_sql_for_clickhouse
from app.infra.sql.validator import validate_clickhouse_sql


def test_normalize_rewrites_date_trunc_month() -> None:
    sql = "SELECT DATE_TRUNC('month', created_at) FROM events"

    normalized = normalize_sql_for_clickhouse(sql)

    assert "toStartOfMonth" in normalized
    assert normalized.startswith("SELECT")


def test_normalize_rewrites_date_trunc_default_interval() -> None:
    sql = "SELECT DATE_TRUNC('day', created_at) FROM events"

    normalized = normalize_sql_for_clickhouse(sql)

    assert "toStartOfInterval" in normalized
    assert "INTERVAL" in normalized


def test_normalize_converts_current_date_variants() -> None:
    normalized = normalize_sql_for_clickhouse("SELECT currentDate()")

    assert normalized == "SELECT today()"


def test_normalize_converts_current_timestamp() -> None:
    normalized = normalize_sql_for_clickhouse("SELECT CURRENT_TIMESTAMP")

    assert normalized == "SELECT now()"


def test_validator_blocks_forbidden_statements() -> None:
    with pytest.raises(SQLNormalizationError, match="Forbidden SQL operation detected"):
        normalize_sql_for_clickhouse("DELETE FROM events")


def test_parsing_error_falls_back_to_raw_select() -> None:
    assert normalize_sql_for_clickhouse("SELECT * FROM") == "SELECT * FROM"


def test_validator_rejects_comments() -> None:
    with pytest.raises(ValueError, match="SQL comments are not permitted"):
        validate_clickhouse_sql("/* comment */ SELECT 1")
