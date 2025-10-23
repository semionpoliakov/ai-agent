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


def test_normalize_closes_unbalanced_double_quotes() -> None:
    sql = 'SELECT "col FROM table'
    normalized = normalize_sql_for_clickhouse(sql)
    assert normalized == 'SELECT "col" FROM table'


def test_normalize_closes_unbalanced_backticks() -> None:
    sql = "SELECT `column FROM table"
    normalized = normalize_sql_for_clickhouse(sql)
    assert normalized == "SELECT `column` FROM table"


def test_normalize_handles_multiline_sql() -> None:
    sql = """
    SELECT
        user_id,
        COUNT(*) AS total
    FROM
        events
    WHERE
        type = 'click'
    GROUP BY
        user_id
    """
    normalized = normalize_sql_for_clickhouse(sql)
    assert "SELECT" in normalized
    assert "GROUP BY" in normalized


def test_normalize_blocks_sql_injection_attempt() -> None:
    malicious_sql = "SELECT * FROM users; DROP TABLE users; --"
    with pytest.raises(SQLNormalizationError, match="Forbidden SQL operation detected"):
        normalize_sql_for_clickhouse(malicious_sql)
