"""In-memory conversation tracking for short-lived history."""

from __future__ import annotations

from collections import deque

from ...infra.config import Settings, get_settings


class ConversationMemory:
    """Stores recent question/answer pairs per user in memory."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._store: dict[str, deque[str]] = {}

    def add(self, user_id: str, message: str) -> None:
        history = self._store.setdefault(user_id, deque(maxlen=self._settings.max_history_messages))
        history.append(message)

    def get_recent(self, user_id: str) -> list[str]:
        history = self._store.get(user_id)
        if not history:
            return []
        return list(history)

    def truncate(self) -> None:
        for key, history in list(self._store.items()):
            if not history:
                self._store.pop(key, None)


_MEMORY: ConversationMemory | None = None


def get_memory() -> ConversationMemory:
    global _MEMORY
    if _MEMORY is None:
        _MEMORY = ConversationMemory()
    return _MEMORY
