"""Prompt loading utilities."""

from __future__ import annotations

from pathlib import Path

_PROMPT_DIR = Path(__file__).resolve().parent


def load_prompt(name: str) -> str:
    """Load a prompt template file from disk."""
    path = _PROMPT_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8")
