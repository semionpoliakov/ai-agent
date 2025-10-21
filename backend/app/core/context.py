from __future__ import annotations

from collections import deque

from .config import get_settings

_settings = get_settings()


class ConversationMemory:
    def __init__(self) -> None:
        self._store: dict[str, deque[str]] = {}

    def add(self, user_id: str, message: str) -> None:
        history = self._store.setdefault(user_id, deque(maxlen=_settings.max_history_messages))
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


def get_memory() -> ConversationMemory:
    return _MEMORY


_MEMORY = ConversationMemory()
