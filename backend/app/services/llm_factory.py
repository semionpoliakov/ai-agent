from __future__ import annotations

import logging
from typing import Protocol

from app.core.config import get_settings
from app.services.llm_client_groq import GroqClient

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    async def generate_text(self, prompt: str) -> str: ...


_clients: dict[str, LLMClient] = {}


def _get_or_create_groq_client() -> LLMClient:
    provider_key = "groq"
    client = _clients.get(provider_key)
    if client is None:
        client = GroqClient()
        _clients[provider_key] = client
    return client


def get_llm_client() -> LLMClient:
    settings = get_settings()
    provider = (settings.llm_provider or "groq").lower()

    if provider == "groq":
        return _get_or_create_groq_client()
    if provider == "openai":
        raise NotImplementedError("OpenAI LLM provider is not implemented yet")
    if provider == "gemini":
        raise NotImplementedError("Gemini LLM provider is no longer supported")

    logger.error("Unsupported LLM provider requested", extra={"provider": provider})
    raise ValueError(f"Unsupported LLM provider '{provider}'")
