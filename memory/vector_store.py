# Memoria de longo prazo: guarda trechos de conversa e permite buscar os mais
# parecidos com um assunto. So e' consultada quando o LLM chama a tool
# recall_memory, entao nao pesa no prompt de toda mensagem.

import json

import numpy as np

from config import settings
from memory.embeddings import embed


class VectorStore:
    def __init__(self, path=None):
        self.path = path or settings.VECTOR_STORE_FILE
        self.entries: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def add(self, text: str) -> None:
        self.entries.append({"text": text, "vector": embed(text).tolist()})
        self._save()

    def search(self, query: str, top_k: int = 3) -> list[str]:
        if not self.entries:
            return []

        query_vec = embed(query)
        scored = [
            (float(np.dot(query_vec, np.array(entry["vector"]))), entry["text"])
            for entry in self.entries
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [text for score, text in scored[:top_k] if score > 0]

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.entries, ensure_ascii=False, indent=2), encoding="utf-8")
