# Historico curto de conversa, persistido em disco. Deliberadamente pequeno -
# o resto vira memoria de longo prazo em vector_store.py, consultada sob
# demanda pelo proprio LLM (tool recall_memory) em vez de ir sempre no prompt.

import json

from config import settings


class ConversationHistory:
    def __init__(self, max_turns: int | None = None, path=None):
        self.max_turns = max_turns or settings.MAX_HISTORY_TURNS
        self.path = path or settings.HISTORY_FILE
        self.turns: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def add(self, role: str, content: str) -> None:
        self.turns.append({"role": role, "content": content})
        self.turns = self.turns[-self.max_turns * 2 :]
        self._save()

    def recent(self) -> list[dict]:
        return list(self.turns)

    def clear(self) -> None:
        self.turns = []
        self._save()

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.turns, ensure_ascii=False, indent=2), encoding="utf-8")
