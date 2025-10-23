"""SQL compatibility layer for ClickHouse using sqlglot."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

import sqlglot
from sqlglot import exp
from sqlglot.errors import SqlglotError
from sqlglot.tokens import TokenType, Tokenizer

from .function_map_loader import FunctionRule, load_function_rules

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
    """Raised when SQL cannot be normalized into valid ClickHouse syntax."""


def normalize_sql_for_clickhouse(sql: str, *, config_path: str | None = None) -> str:
    """Normalize generic SQL into ClickHouse-compatible SQL."""
    sql_input = (sql or "").strip()
    if not sql_input:
        raise SQLNormalizationError("Empty SQL statement")

    sanitized_input = _sanitize_unbalanced_quotes(sql_input)
    preprocessed_sql = _preprocess_sql(sanitized_input)
    preprocessed_sql = _sanitize_unbalanced_quotes(preprocessed_sql)

    try:
        parsed = sqlglot.parse_one(preprocessed_sql)
    except SqlglotError as exc:
        logger.warning("SQLNormalizer: parse_failed error=%s sql=%r", exc, sql_input)
        if preprocessed_sql.strip().upper().startswith("SELECT"):
            logger.warning(
                "SQLNormalizer: fallback_to_raw_sql reason=parse_failed sql=%s",
                preprocessed_sql,
            )
            from .validator import validate_clickhouse_sql

            try:
                return validate_clickhouse_sql(preprocessed_sql)
            except ValueError as validation_error:
                raise SQLNormalizationError(str(validation_error)) from validation_error
        raise SQLNormalizationError("Unable to parse SQL") from exc

    rules = load_function_rules(Path(config_path)) if config_path else load_function_rules()
    rewritten = _rewrite_functions(parsed, rules)
    cleaned = _strip_unsupported_constructs(rewritten)

    try:
        normalized_sql = cleaned.sql(dialect="clickhouse")
    except SqlglotError as exc:
        logger.warning("SQLNormalizer: render_failed error=%s sql=%r", exc, sql_input)
        raise SQLNormalizationError("Unable to render SQL for ClickHouse") from exc

    normalized_sql = normalized_sql.strip()

    from .validator import validate_clickhouse_sql  # lazy import to avoid circular dependency

    try:
        return validate_clickhouse_sql(normalized_sql)
    except ValueError as exc:
        raise SQLNormalizationError(str(exc)) from exc


def _rewrite_functions(expression: exp.Expression, rules: Sequence[FunctionRule]) -> exp.Expression:
    if not rules:
        return expression

    def _transform(expr: exp.Expression) -> exp.Expression:
        if isinstance(expr, exp.Func):
            return _apply_rules(expr, rules)
        return expr

    return expression.transform(_transform)


def _apply_rules(function_expr: exp.Func, rules: Sequence[FunctionRule]) -> exp.Expression:
    if isinstance(function_expr, exp.Anonymous):
        raw_name = function_expr.name
    else:
        raw_name = function_expr.sql_name()
    function_name = (raw_name or "").upper()
    args, context = _build_context(function_expr)

    for rule in rules:
        if not rule.matches(function_name, context):
            continue
        try:
            rendered_sql = rule.template.format_map(context)
        except KeyError as exc:
            logger.warning(
                "SQLNormalizer: template_missing_context function=%s missing_key=%s",
                function_name,
                exc,
            )
            continue
        try:
            replacement = sqlglot.parse_one(rendered_sql, read="clickhouse")
        except SqlglotError as exc:
            logger.warning(
                "SQLNormalizer: replacement_parse_failed function=%s template=%s error=%s",
                function_name,
                rendered_sql,
                exc,
            )
            continue

        _carry_metadata(function_expr, replacement)
        logger.debug("SQLNormalizer: replaced %s -> %s", function_name, rendered_sql)
        return replacement

    return function_expr


def _build_context(function_expr: exp.Func) -> tuple[list[exp.Expression], dict[str, str]]:
    args = _collect_arguments(function_expr)
    context: dict[str, str] = {"arg_count": str(len(args))}
    for index, argument in enumerate(args):
        sql_representation = argument.sql(dialect="clickhouse")
        context[f"args{index}"] = sql_representation

        literal_value = _literal_value(argument)
        if literal_value is not None:
            context[f"args{index}_value"] = literal_value
            context[f"args{index}_value_lower"] = literal_value.lower()
            context[f"args{index}_value_upper"] = literal_value.upper()
    for key, value in function_expr.args.items():
        if isinstance(value, exp.Expression):
            context[key] = value.sql(dialect="clickhouse")
            literal_value = _literal_value(value)
            if literal_value is not None:
                context[f"{key}_value"] = literal_value
                context[f"{key}_value_lower"] = literal_value.lower()
                context[f"{key}_value_upper"] = literal_value.upper()
    return args, context


def _collect_arguments(function_expr: exp.Func) -> list[exp.Expression]:
    positional = list(function_expr.expressions or [])
    if positional:
        return positional

    expressions_arg = function_expr.args.get("expressions")
    if isinstance(expressions_arg, (list, tuple)):
        return list(expressions_arg)

    collected: list[exp.Expression] = []
    for key in getattr(function_expr, "arg_types", {}) or {}:
        value = function_expr.args.get(key)
        if isinstance(function_expr, exp.Anonymous) and key == "this":
            continue
        if isinstance(value, exp.Expression):
            collected.append(value)
    return collected


def _literal_value(argument: exp.Expression) -> str | None:
    if isinstance(argument, exp.Literal):
        return argument.this
    if isinstance(argument, exp.Identifier):
        return argument.name
    return None


def _carry_metadata(source: exp.Expression, target: exp.Expression) -> None:
    for key, value in source.args.items():
        if key in {"this", "expressions"} or value is None:
            continue
        target.set(key, value)


def _strip_unsupported_constructs(expression: exp.Expression) -> exp.Expression:
    def _transform(expr: exp.Expression) -> exp.Expression:
        if isinstance(expr, exp.Group) and expr.args.get("rollup"):
            logger.debug("SQLNormalizer: removed WITH ROLLUP clause")
            expr = expr.copy()
            expr.set("rollup", None)
            return expr
        return expr

    return expression.transform(_transform)


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
    logger.debug("SQLNormalizer: removed AS OF clause count=%d", len(spans))
    return cleaned
def _sanitize_unbalanced_quotes(sql: str) -> str:
    if not sql:
        return sql

    single_count = sql.count("'")
    double_count = sql.count('"')
    fixed_sql = sql
    fixed = False

    if single_count % 2:
        fixed_sql += "'"
        fixed = True
    if double_count % 2:
        fixed_sql += '"'
        fixed = True

    if fixed:
        logger.debug(
            "SQLNormalizer: fixed_unbalanced_quotes single_quotes=%d double_quotes=%d",
            single_count,
            double_count,
        )
    return fixed_sql
