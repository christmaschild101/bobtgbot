"""JSON-file persistence for per-group settings."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

DEFAULT_WELCOME = "Welcome to %groupname%! Hope you have a grait time!"
DEFAULT_FAREWELL = "And there they go! Good bye <name>."


class BobStore:
    """Stores per-chat settings in a single JSON file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self._data: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._data = {}
        if not isinstance(self._data, dict):
            self._data = {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        tmp.replace(self.path)

    def _chat(self, chat_id: int) -> dict[str, Any]:
        key = str(chat_id)
        if key not in self._data:
            self._data[key] = {
                "welcome_msg": DEFAULT_WELCOME,
                "farewell_msg": DEFAULT_FAREWELL,
            }
        return self._data[key]

    def get_welcome(self, chat_id: int) -> str:
        with self._lock:
            return str(self._chat(chat_id)["welcome_msg"])

    def set_welcome(self, chat_id: int, message: str) -> None:
        with self._lock:
            self._chat(chat_id)["welcome_msg"] = message
            self._save()

    def get_farewell(self, chat_id: int) -> str:
        with self._lock:
            return str(self._chat(chat_id)["farewell_msg"])

    def set_farewell(self, chat_id: int, message: str) -> None:
        with self._lock:
            self._chat(chat_id)["farewell_msg"] = message
            self._save()