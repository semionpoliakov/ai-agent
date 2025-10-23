"""Protocol definitions for interacting with LLM providers."""

from __future__ import annotations

from typing import Protocol


class LLMClientProtocol(Protocol):
    """Minimal surface required by the orchestrator for text generation."""

    async def generate_text(self, prompt: str, *, temperature: float | None = None) -> str:
        """Generate a text completion for the given prompt."""
        raise NotImplementedError
