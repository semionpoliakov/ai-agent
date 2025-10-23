"""Groq LLM client adapter."""

from __future__ import annotations

import asyncio
from typing import cast

from groq import Groq

from ..config import Settings, get_settings
from .base import LLMClientProtocol


class GroqClient(LLMClientProtocol):
    """Concrete implementation of `LLMClientProtocol` backed by Groq."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        secret = self._settings.llm_api_key
        if secret is None:
            raise RuntimeError("LLM_API_KEY is required for Groq client initialisation")
        self._model = self._settings.llm_model
        self._temperature = self._settings.llm_temperature
        self._client = Groq(api_key=secret.get_secret_value())

    async def generate_text(self, prompt: str, *, temperature: float | None = None) -> str:
        def _invoke() -> str:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature if temperature is None else temperature,
            )
            choices = completion.choices or []
            if not choices:
                raise RuntimeError("Groq completion returned no choices")
            message = choices[0].message
            content = cast(str | None, getattr(message, "content", None))
            if not content:
                raise RuntimeError("Groq completion returned empty message content")
            return content.strip()

        return await asyncio.to_thread(_invoke)
