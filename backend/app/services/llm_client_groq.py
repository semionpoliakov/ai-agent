from __future__ import annotations

import asyncio

from groq import Groq

from app.core.config import get_settings


class GroqClient:
    def __init__(self) -> None:
        settings = get_settings()
        secret = settings.groq_api_key
        if secret is None:
            raise RuntimeError("GROQ_API_KEY is required when LLM_PROVIDER is set to 'groq'")
        self._model = settings.llm_model
        self._client = Groq(api_key=secret.get_secret_value())

    async def generate_text(self, prompt: str) -> str:
        def _invoke() -> str:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
            )
            choices = completion.choices or []
            if not choices:
                raise RuntimeError("Groq completion returned no choices")
            message = choices[0].message
            content = getattr(message, "content", None)
            if not content:
                raise RuntimeError("Groq completion returned empty message content")
            return content.strip()

        return await asyncio.to_thread(_invoke)
