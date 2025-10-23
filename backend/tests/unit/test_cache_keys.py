from __future__ import annotations

from app.infra.cache import keys


def test_normalize_sql_collapses_whitespace() -> None:
    assert keys.normalize_sql(" SELECT  *\nFROM  table ") == "SELECT * FROM table"


def test_fingerprint_deterministic() -> None:
    first = keys.fingerprint("question", "SELECT * FROM t")
    second = keys.fingerprint("question", "SELECT   *  FROM   t\n")
    assert first == second


def test_question_key_case_insensitive() -> None:
    assert keys.question_key("Hello") == keys.question_key("hello")
