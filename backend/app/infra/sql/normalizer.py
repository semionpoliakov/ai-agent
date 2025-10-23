from __future__ import annotations

import logging
from sqlglot import exp
from sqlglot.errors import SqlglotError
from sqlglot.tokens import TokenType, Tokenizer
import sqlglot

logger = logging.getLogger(__name__)

_CLAUSE_BOUNDARIES = {
    TokenType.WHERE,
    TokenType.GROUP_BY,
    TokenType.ORDER_BY,
    TokenType.LIMIT,
    TokenType.HAVING,
    TokenType.QUALIFY,
    TokenType.WINDOW,
    TokenType.JOIN,
    TokenType.RIGHT,
    TokenType.LEFT,
    TokenType.FULL,
    TokenType.CROSS,
    TokenType.INNER,
    TokenType.OUTER,
    TokenType.UNION,
    TokenType.EXCEPT,
    TokenType.INTERSECT,
    TokenType.SEMI,
    TokenType.ANTI,
    TokenType.ON,
    TokenType.R_PAREN,
    TokenType.COMMA,
}


class SQLNormalizationError(ValueError):
    pass


def normalize_sql_for_clickhouse(sql: str) -> str:
    sql_input = (sql or "").strip()
    if not sql_input:
        raise SQLNormalizationError("Empty SQL statement")

    sanitized_input = _sanitize_unbalanced_quotes(sql_input)
    preprocessed_sql = _preprocess_sql(sanitized_input)
    preprocessed_sql = _sanitize_unbalanced_quotes(preprocessed_sql)
    _ensure_single_statement(preprocessed_sql)

    normalized_sql = _try_transpile_to_clickhouse(preprocessed_sql)
    if normalized_sql is None:
        try:
            parsed = sqlglot.parse_one(preprocessed_sql)
            normalized_sql = parsed.sql(dialect="clickhouse")
        except SqlglotError as exc:
            logger.warning("SQLNormalizer: parse_failed error=%s sql=%r", exc, sql_input)
            if preprocessed_sql.strip().upper().startswith("SELECT"):
                from .validator import validate_clickhouse_sql
                try:
                    return validate_clickhouse_sql(preprocessed_sql)
                except ValueError as validation_error:
                    raise SQLNormalizationError(str(validation_error)) from validation_error
            raise SQLNormalizationError("Unable to parse SQL") from exc

    normalized_sql = normalized_sql.strip()
    _ensure_single_statement(normalized_sql)

    from .validator import validate_clickhouse_sql
    try:
        return validate_clickhouse_sql(normalized_sql)
    except ValueError as exc:
        raise SQLNormalizationError(str(exc)) from exc


def _try_transpile_to_clickhouse(sql_text: str) -> str | None:
    for read_dialect in ("mysql", "postgres", "sqlite"):
        try:
            parts = sqlglot.transpile(sql_text, read=read_dialect, write="clickhouse")
            if parts and parts[0].strip():
                return parts[0]
        except SqlglotError:
            continue
    return None


def _preprocess_sql(sql: str) -> str:
    tokens = list(Tokenizer().tokenize(sql))
    if not tokens:
        return sql

    spans: list[tuple[int, int]] = []
    index = 0
    length = len(tokens)
    while index < length - 1:
        token = tokens[index]
        if token.token_type == TokenType.ALIAS and token.text.upper() == "AS":
            next_token = tokens[index + 1]
            if next_token.token_type == TokenType.VAR and next_token.text.upper() == "OF":
                start = token.start
                end = next_token.end
                cursor = index + 2
                while cursor < length:
                    lookahead = tokens[cursor]
                    if lookahead.token_type in _CLAUSE_BOUNDARIES:
                        break
                    end = lookahead.end
                    cursor += 1
                spans.append((start, end))
                index = cursor
                continue
        index += 1

    if not spans:
        return sql

    result_parts: list[str] = []
    last_position = 0
    for start, end in spans:
        prefix = sql[last_position:start]
        if prefix:
            result_parts.append(prefix)
            if not prefix[-1].isspace():
                result_parts.append(" ")
        last_position = end + 1
        if last_position < len(sql) and not sql[last_position].isspace():
            result_parts.append(" ")
    result_parts.append(sql[last_position:])
    cleaned = "".join(result_parts)
    return cleaned


def _sanitize_unbalanced_quotes(sql: str) -> str:
    if not sql:
        return sql

    def _close_unbalanced(s: str, quote: str) -> str:
        count = s.count(quote)
        if count % 2 == 0:
            return s
        start = s.rfind(quote)
        if start == -1:
            return s
        end = start + 1
        while end < len(s) and s[end] not in {" ", "\t", "\n", ",", ";"}:
            end += 1
        return s[:end] + quote + s[end:]

    sql = _close_unbalanced(sql, "'")
    sql = _close_unbalanced(sql, '"')
    sql = _close_unbalanced(sql, "`")
    return sql


def _ensure_single_statement(sql: str) -> None:
    tokenizer = Tokenizer()
    tokens = list(tokenizer.tokenize(sql))
    seen_semicolon = False
    for tok in tokens:
        if tok.token_type == TokenType.SEMICOLON:
            seen_semicolon = True
            continue
        if not seen_semicolon:
            continue
        if tok.token_type in (TokenType.SEMICOLON, TokenType.COMMENT):
            continue
        if tok.text.strip() == "":
            continue
        raise SQLNormalizationError("Forbidden SQL operation detected")
