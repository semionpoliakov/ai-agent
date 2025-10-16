from __future__ import annotations

import asyncio
from typing import Any

import httpx

from ..core.config import get_settings


class GeminiClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._model = settings.gemini_model
        self._api_key = settings.gemini_api_key.get_secret_value()
        self._client = httpx.AsyncClient(
            base_url="https://generativelanguage.googleapis.com/v1beta",
            timeout=httpx.Timeout(30.0, read=60.0),
        )
        self._lock = asyncio.Lock()

    async def generate_text(self, prompt: str) -> str:
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ]
        }
        async with self._lock:
            response = await self._client.post(
                f"/models/{self._model}:generateContent",
                params={"key": self._api_key},
                json=payload,
            )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError("Gemini response is empty")
        parts = candidates[0].get("content", {}).get("parts") or []
        if not parts:
            raise RuntimeError("Gemini response parts missing")
        text = parts[0].get("text")
        if not text:
            raise RuntimeError("Gemini response text missing")
        return text.strip()

    async def close(self) -> None:
        await self._client.aclose()


_gemini_client: GeminiClient | None = None


def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
