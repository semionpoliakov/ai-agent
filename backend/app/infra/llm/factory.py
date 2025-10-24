"""Factory for LLM client implementations."""

from __future__ import annotations

from ..config import Settings, get_settings
from .base import LLMClientProtocol
from .groq_client import GroqClient


class ProviderNotConfiguredError(RuntimeError):
    """Raised when an unsupported or unconfigured LLM provider is requested."""


def get_llm_client(settings: Settings | None = None) -> LLMClientProtocol:
    """Return a configured LLM client."""
    settings = settings or get_settings()
    provider = (settings.llm_provider or "groq").lower()

    if provider == "groq":
        return GroqClient(settings)
    if provider == "openai":
        raise ProviderNotConfiguredError("OpenAI provider is not yet configured")
    if provider == "vertex":
        raise ProviderNotConfiguredError("Vertex provider is not yet configured")

    raise ProviderNotConfiguredError(f"Unsupported LLM provider '{provider}'")
