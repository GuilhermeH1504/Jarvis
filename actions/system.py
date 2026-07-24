# Acoes de sistema. Desligar/reiniciar exigem confirmacao explicita
# (confirm=True) por serem destrutivas e dificeis de reverter - o graph.py so
# passa confirm=True depois que o usuario confirma no turno seguinte.

import ctypes
import subprocess


def lock() -> str:
    ctypes.windll.user32.LockWorkStation()
    return "Computador bloqueado."


def shutdown(confirm: bool = False) -> str:
    if not confirm:
        return "Tem certeza que quer desligar o computador? Confirme pra eu executar."

    subprocess.run(["shutdown", "/s", "/t", "5"], check=False)
    return "Desligando o computador em 5 segundos."


def restart(confirm: bool = False) -> str:
    if not confirm:
        return "Tem certeza que quer reiniciar o computador? Confirme pra eu executar."

    subprocess.run(["shutdown", "/r", "/t", "5"], check=False)
    return "Reiniciando o computador em 5 segundos."
