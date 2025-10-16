from __future__ import annotations

import pytest

from backend.app.services.sql_validator import allow_only_select


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM ad_performance",
        "\n -- comment\n SELECT source, sum(spend) FROM ad_performance GROUP BY source",
    ],
)
def test_allow_select_queries(query: str) -> None:
    assert allow_only_select(query).startswith("SELECT")


@pytest.mark.parametrize(
    "query",
    [
        "INSERT INTO ad_performance VALUES (...)",
        "DELETE FROM ad_performance WHERE 1=1",
        "SELECT 1; DROP TABLE ad_performance",
        "",
    ],
)
def test_disallow_non_select(query: str) -> None:
    with pytest.raises(ValueError):
        allow_only_select(query)
