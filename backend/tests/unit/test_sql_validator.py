from __future__ import annotations

import pytest
from app.domain.services.sql_validator import validate_sql_is_safe
from hypothesis import given
from hypothesis import strategies as st


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM ad_performance",
        "SELECT source, sum(spend) FROM ad_performance GROUP BY source",
    ],
)
def test_validate_sql_allows_select_queries(query: str) -> None:
    assert validate_sql_is_safe(query).startswith("SELECT")


@pytest.mark.parametrize(
    "query",
    [
        "INSERT INTO ad_performance VALUES (...)",
        "DELETE FROM ad_performance WHERE 1=1",
        "SELECT 1; DROP TABLE ad_performance",
        "/* comment */ SELECT 1",
        "",
    ],
)
def test_validate_sql_rejects_unsafe_queries(query: str) -> None:
    with pytest.raises(ValueError):
        validate_sql_is_safe(query)


@given(st.text(alphabet=st.characters(blacklist_characters=";"), min_size=1, max_size=64))
def test_validate_sql_rejects_appended_statements(random_suffix: str) -> None:
    with pytest.raises(ValueError):
        validate_sql_is_safe(f"SELECT 1; {random_suffix}")
