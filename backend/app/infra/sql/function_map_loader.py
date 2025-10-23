"""Load SQL function normalization rules from configuration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent.parent / "config" / "sql_function_map.yaml"
)


@dataclass(frozen=True)
class FunctionRule:
    """Single function rewriting rule derived from configuration."""

    function: str
    template: str
    conditions: dict[str, str]

    def matches(self, function_name: str, context: dict[str, str]) -> bool:
        if function_name != self.function:
            return False
        return all(context.get(key) == value for key, value in self.conditions.items())


def _ensure_mapping(raw_rule: Any) -> dict[str, Any]:
    if not isinstance(raw_rule, dict):
        raise ValueError(f"Invalid function rule entry, expected mapping but got {type(raw_rule)!r}")
    return raw_rule


def _coerce_conditions(raw_conditions: Any) -> dict[str, str]:
    if raw_conditions is None:
        return {}
    if not isinstance(raw_conditions, dict):
        raise ValueError(
            f"Invalid 'when' entry for function rule, expected mapping but got {type(raw_conditions)!r}"
        )
    coerced: dict[str, str] = {}
    for key, value in raw_conditions.items():
        if value is None:
            continue
        coerced[str(key)] = str(value)
    return coerced


def _parse_rule(raw_rule: dict[str, Any]) -> FunctionRule:
    try:
        function = str(raw_rule["function"]).upper()
    except KeyError as exc:
        raise ValueError("Missing 'function' key in function rule entry") from exc
    try:
        template = str(raw_rule["template"])
    except KeyError as exc:
        raise ValueError(f"Missing 'template' for function '{function}'") from exc

    conditions = _coerce_conditions(raw_rule.get("when"))
    return FunctionRule(function=function, template=template, conditions=conditions)


def _load_yaml(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("SQL function map configuration must be a mapping")
    return data


@lru_cache(maxsize=1)
def load_function_rules(config_path: Path | None = None) -> tuple[FunctionRule, ...]:
    """Read function rewriting rules from YAML configuration."""
    path = config_path or DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"SQL function map configuration not found: {path}")

    raw_config = _load_yaml(path)
    raw_rules = raw_config.get("function_rules", [])
    if not isinstance(raw_rules, list):
        raise ValueError("`function_rules` must be a list of function rule entries")

    rules = tuple(_parse_rule(_ensure_mapping(raw_rule)) for raw_rule in raw_rules)
    logger.debug("SQLNormalizer: loaded_function_rules count=%d path=%s", len(rules), path)
    return rules
