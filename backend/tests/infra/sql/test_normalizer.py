from __future__ import annotations

import pytest

from app.infra.sql.normalizer import SQLNormalizationError, normalize_sql_for_clickhouse


def test_normalize_closes_unbalanced_quotes() -> None:
    sql = "SELECT * FROM events WHERE source = 'fac"

    normalized = normalize_sql_for_clickhouse(sql)

    assert normalized == "SELECT * FROM events WHERE source = 'fac'"


def test_normalize_fallback_returns_select_on_parse_error() -> None:
    sql = "SELECT * FROM events WHERE )"

    normalized = normalize_sql_for_clickhouse(sql)

    assert normalized == "SELECT * FROM events WHERE )"


def test_normalize_rejects_non_select_statements() -> None:
    with pytest.raises(SQLNormalizationError, match="Forbidden SQL operation detected"):
        normalize_sql_for_clickhouse("INSERT INTO events VALUES (1)")
