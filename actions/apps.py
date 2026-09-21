# Abre aplicativos comuns do Windows a partir de um nome falado/digitado.
# So abre apps conhecidos (sem shell=True com texto livre) pra nao correr
# risco de injecao de comando via fala mal transcrita.

import difflib
import os
import re
import unicodedata

APP_ALIASES = {
    "bloco de notas": "notepad.exe",
    "notepad": "notepad.exe",
    "calculadora": "calc.exe",
    "explorador de arquivos": "explorer.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "terminal": "wt.exe",
    "spotify": "spotify.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "navegador": "chrome.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
}

# Aproximacao minima aceita pra tolerar erro de transcricao ("calculadora" -> "calculadura").
_FUZZY_CUTOFF = 0.85


def _normalize(text: str) -> str:
    # Minusculo, sem acento e sem pontuacao: "Calculadóra!" -> "calculadora".
    decomposed = unicodedata.normalize("NFD", text.lower())
    no_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^\w\s]", "", no_accents).strip()


_NORMALIZED_ALIASES = {_normalize(alias): exe for alias, exe in APP_ALIASES.items()}


def _find_executable(name: str) -> str | None:
    key = _normalize(name)
    if key in _NORMALIZED_ALIASES:
        return _NORMALIZED_ALIASES[key]

    close = difflib.get_close_matches(key, _NORMALIZED_ALIASES, n=1, cutoff=_FUZZY_CUTOFF)
    return _NORMALIZED_ALIASES[close[0]] if close else None


def open_app(name: str) -> str:
    executable = _find_executable(name)

    if not executable:
        return f"Não conheço o aplicativo '{name}'. Adicione um alias em actions/apps.py."

    try:
        os.startfile(executable)
        return f"Abrindo {name}."
    except OSError:
        return f"Não consegui abrir '{name}'. Verifique se está instalado."
