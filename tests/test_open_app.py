# Testa a interpretacao de "abrir <app>" (router + resolucao de alias), sem abrir nada.

import pytest

from actions.apps import _find_executable
from brain.router import route


@pytest.mark.parametrize(
    "phrase, expected",
    [
        ("abrir o bloco de notas", "bloco de notas"),
        ("abre a calculadora", "calculadora"),
        ("abra o chrome", "chrome"),
        ("Abrir o Chrome.", "Chrome"),
        ("abre o spotify, por favor", "spotify"),
        ("Jarvis, por favor, abre o excel!", "excel"),
        ("abrir opera", "opera"),
        ("abrir a", "a"),
    ],
)
def test_route_extracts_app_name(phrase, expected):
    intent = route(phrase)
    assert intent.action == "open_app"
    assert intent.args["value"] == expected


def test_route_keeps_normal_chat_as_chat():
    assert route("que horas sao").kind == "chat"


@pytest.mark.parametrize(
    "name, executable",
    [
        ("Chrome", "chrome.exe"),
        ("CALCULADORA", "calc.exe"),
        ("calculadóra", "calc.exe"),
        ("bloco de notas.", "notepad.exe"),
        ("calculadura", "calc.exe"),
        ("excell", "excel.exe"),
    ],
)
def test_find_executable_is_tolerant(name, executable):
    assert _find_executable(name) == executable


@pytest.mark.parametrize("name", ["opera", "discord", "", "xyz"])
def test_find_executable_rejects_unknown_apps(name):
    assert _find_executable(name) is None
