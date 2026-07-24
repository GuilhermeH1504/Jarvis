# Decide, sem gastar tokens de LLM, se a fala do usuario e um comando de
# sistema direto (abrir app, bloquear/desligar o pc) ou uma conversa normal
# que deve ir pro LLM (com acesso as tools em brain/tools.py).

import re
from dataclasses import dataclass, field


@dataclass
class Intent:
    kind: str  # "chat" ou "action"
    action: str = ""
    args: dict = field(default_factory=dict)


_PATTERNS = [
    ("lock", re.compile(r"^(?:bloquear|travar)\s+(?:o\s+)?(?:computador|pc)", re.IGNORECASE)),
    ("shutdown", re.compile(r"^desligar\s+(?:o\s+)?(?:computador|pc)", re.IGNORECASE)),
    ("restart", re.compile(r"^reiniciar\s+(?:o\s+)?(?:computador|pc)", re.IGNORECASE)),
    ("open_app", re.compile(r"^abr[ei]r?\s+(?:o|a)?\s*(.+)", re.IGNORECASE)),
]


def route(user_input: str) -> Intent:
    text = user_input.strip()

    for action, pattern in _PATTERNS:
        match = pattern.match(text)
        if not match:
            continue

        args = {}
        if match.groups():
            args["value"] = match.group(1).strip()

        return Intent(kind="action", action=action, args=args)

    return Intent(kind="chat")
