# Abre aplicativos comuns do Windows a partir de um nome falado/digitado.
# So abre apps conhecidos (sem shell=True com texto livre) pra nao correr
# risco de injecao de comando via fala mal transcrita.

import os

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
    "navegador": "chrome.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
}


def open_app(name: str) -> str:
    key = name.strip().lower()
    executable = APP_ALIASES.get(key)

    if not executable:
        return f"Não conheço o aplicativo '{name}'. Adicione um alias em actions/apps.py."

    try:
        os.startfile(executable)
        return f"Abrindo {name}."
    except OSError:
        return f"Não consegui abrir '{name}'. Verifique se está instalado."
