"""Factory for LLM client implementations."""

from __future__ import annotations

from ..config import Settings, get_settings
from .base import LLMClientProtocol
from .groq_client import GroqClient

_CLIENTS: dict[str, LLMClientProtocol] = {}


class ProviderNotConfiguredError(RuntimeError):
    """Raised when an unsupported or unconfigured LLM provider is requested."""


def _get_or_create_groq(settings: Settings) -> LLMClientProtocol:
    client = _CLIENTS.get("groq")
    if client is None:
        client = GroqClient(settings)
        _CLIENTS["groq"] = client
    return client


def get_llm_client(settings: Settings | None = None) -> LLMClientProtocol:
    """Return a configured LLM client."""
    settings = settings or get_settings()
    provider = (settings.llm_provider or "groq").lower()

    if provider == "groq":
        return _get_or_create_groq(settings)
    if provider == "openai":
        raise ProviderNotConfiguredError("OpenAI provider is not yet configured")
    if provider == "vertex":
        raise ProviderNotConfiguredError("Vertex provider is not yet configured")

    raise ProviderNotConfiguredError(f"Unsupported LLM provider '{provider}'")
