# Testa ReminderStore, ReminderWatcher e as tools de lembrete, sem tocar em data/.

import threading
from datetime import datetime, timedelta

import pytest

from actions.reminders import ReminderStore, ReminderWatcher
from brain.tools import TOOL_SCHEMAS, build_dispatch
from memory.profile import UserProfile


@pytest.fixture
def store(tmp_path):
    return ReminderStore(tmp_path / "reminders.json")


@pytest.fixture
def dispatch(tmp_path, store):
    return build_dispatch(UserProfile(tmp_path / "profile.json"), None, store)


def test_list_pending_is_sorted_by_due(store):
    now = datetime.now()
    store.add("depois", now + timedelta(hours=2))
    store.add("antes", now + timedelta(hours=1))

    assert [r["message"] for r in store.list_pending()] == ["antes", "depois"]


def test_pop_due_returns_only_expired_and_does_not_repeat(store):
    now = datetime.now()
    store.add("passado", now - timedelta(minutes=1))
    store.add("futuro", now + timedelta(hours=1))

    assert [r["message"] for r in store.pop_due()] == ["passado"]
    assert store.pop_due() == []
    assert [r["message"] for r in store.list_pending()] == ["futuro"]


def test_reminders_survive_reload_from_disk(store):
    store.add("guardado", datetime.now() + timedelta(hours=1))

    reloaded = ReminderStore(store.path)

    assert [r["message"] for r in reloaded.list_pending()] == ["guardado"]


def test_cancel_removes_existing_and_rejects_unknown(store):
    reminder = store.add("x", datetime.now() + timedelta(hours=1))

    assert store.cancel("inexistente") is False
    assert store.cancel(reminder["id"]) is True
    assert store.list_pending() == []


def test_watcher_fires_due_reminder_and_stops_cleanly(store):
    store.add("agora", datetime.now() - timedelta(seconds=1))
    fired = threading.Event()
    messages = []

    def on_due(reminder):
        messages.append(reminder["message"])
        fired.set()

    watcher = ReminderWatcher(store, on_due, interval=0.05)
    watcher.start()

    assert fired.wait(timeout=2)
    watcher.stop()

    assert messages == ["agora"]
    assert not watcher._thread.is_alive()


def test_every_tool_schema_has_a_handler(dispatch):
    assert {t["function"]["name"] for t in TOOL_SCHEMAS} == set(dispatch)


def test_create_reminder_in_minutes(dispatch, store):
    result = dispatch["create_reminder"]({"message": "agua", "in_minutes": 10})

    assert "Lembrete criado" in result
    assert len(store.list_pending()) == 1


def test_create_reminder_at_iso_datetime(dispatch, store):
    at = (datetime.now() + timedelta(days=1)).replace(microsecond=0).isoformat()

    result = dispatch["create_reminder"]({"message": "reuniao", "at": at})

    assert "Lembrete criado" in result
    assert store.list_pending()[0]["due"] == at


@pytest.mark.parametrize(
    "args, expected",
    [
        ({"message": "x", "at": "amanha as 9h"}, "inválido"),
        ({"message": "x", "at": "2020-01-01T10:00:00"}, "já passou"),
        ({"message": "x", "in_minutes": -5}, "já passou"),
        ({"message": "x"}, "informe"),
    ],
)
def test_create_reminder_rejects_bad_input_without_saving(dispatch, store, args, expected):
    assert expected in dispatch["create_reminder"](args)
    assert store.list_pending() == []


def test_list_and_cancel_reminders_through_tools(dispatch, store):
    assert "não tem lembretes" in dispatch["list_reminders"]({})

    reminder = store.add("agua", datetime.now() + timedelta(hours=1))
    assert reminder["id"] in dispatch["list_reminders"]({})

    assert "cancelado" in dispatch["cancel_reminder"]({"reminder_id": reminder["id"]})
    assert "Não encontrei" in dispatch["cancel_reminder"]({"reminder_id": reminder["id"]})
