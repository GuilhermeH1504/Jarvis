# Fatos permanentes sobre o usuario (nome, preferencias, etc), persistidos
# em disco e injetados no prompt de sistema em toda conversa.

import json

from config import settings


class UserProfile:
    def __init__(self, path=None):
        self.path = path or settings.PROFILE_FILE
        self.facts: dict[str, str] = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def remember(self, key: str, value: str) -> None:
        self.facts[key] = value
        self._save()

    def forget(self, key: str) -> None:
        self.facts.pop(key, None)
        self._save()

    def as_context_string(self) -> str:
        if not self.facts:
            return ""
        return "\n".join(f"- {key}: {value}" for key, value in self.facts.items())

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.facts, ensure_ascii=False, indent=2), encoding="utf-8")
