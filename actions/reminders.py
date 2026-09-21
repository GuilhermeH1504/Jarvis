# Lembretes persistidos em disco: guarda o que o usuario pediu pra ser
# lembrado e quando, e informa quais ja venceram.

import json
import threading
import uuid
from datetime import datetime

from config import settings


class ReminderStore:
    def __init__(self, path=None):
        self.path = path or settings.REMINDERS_FILE
        self._lock = threading.Lock()
        self.reminders: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save(self) -> None:
        self.path.write_text(
            json.dumps(self.reminders, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def add(self, message: str, due: datetime) -> dict:
        reminder = {
            "id": uuid.uuid4().hex[:6],
            "message": message,
            "due": due.isoformat(timespec="seconds"),
        }
        with self._lock:
            self.reminders.append(reminder)
            self._save()
        return reminder

    def list_pending(self) -> list[dict]:
        with self._lock:
            return sorted(self.reminders, key=lambda r: r["due"])

    def cancel(self, reminder_id: str) -> bool:
        with self._lock:
            remaining = [r for r in self.reminders if r["id"] != reminder_id]
            if len(remaining) == len(self.reminders):
                return False
            self.reminders = remaining
            self._save()
            return True

    def pop_due(self, now: datetime | None = None) -> list[dict]:
        """Remove e devolve os lembretes que ja venceram."""
        now = now or datetime.now()
        with self._lock:
            due = [r for r in self.reminders if datetime.fromisoformat(r["due"]) <= now]
            if due:
                self.reminders = [r for r in self.reminders if r not in due]
                self._save()
            return due


class ReminderWatcher:
    """Confere os lembretes de tempos em tempos numa thread e avisa os vencidos."""

    def __init__(self, store: ReminderStore, on_due, interval: float = 1.0):
        self.store = store
        self.on_due = on_due
        self.interval = interval
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        while not self._stop.is_set():
            for reminder in self.store.pop_due():
                self.on_due(reminder)
            self._stop.wait(self.interval)