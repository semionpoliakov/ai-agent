from __future__ import annotations

import pytest
from app.domain.services import sql_builder


def test_strip_think_blocks_removes_tags() -> None:
    text = "<think>internal reasoning</think> SELECT 1"
    assert sql_builder.strip_think_blocks(text) == "SELECT 1"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("```sql\nSELECT 1\n```", "SELECT 1"),
        ("```SELECT 2```", "SELECT 2"),
        ("SELECT 3", "SELECT 3"),
    ],
)
def test_strip_code_fences_handles_markdown(raw: str, expected: str) -> None:
    assert sql_builder.strip_code_fences(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("SELECT 1;", "SELECT 1"),
        ("SELECT 1;;", "SELECT 1"),
        ("SELECT 1", "SELECT 1"),
    ],
)
def test_trim_trailing_semicolons(raw: str, expected: str) -> None:
    assert sql_builder.trim_trailing_semicolons(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("```sql\n<think>ignore</think> SELECT * FROM t;```", "SELECT * FROM t"),
        ("SQL: SELECT `col` FROM `t`;", "SELECT col FROM t"),
        ('"SELECT * FROM t;"', "SELECT * FROM t"),
    ],
)
def test_clean_sql_output_normalises(raw: str, expected: str) -> None:
    assert sql_builder.clean_sql_output(raw) == expected
