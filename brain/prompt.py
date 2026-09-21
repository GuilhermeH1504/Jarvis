# Monta as mensagens enviadas ao LLM a partir da persona, do perfil e do
# historico curto de conversa.

from brain.prompts import PERSONA_SYSTEM_PROMPT, PROFILE_CONTEXT_TEMPLATE
from datetime import datetime


def build_messages(history: list[dict], user_input: str, profile_facts: str = "") -> list[dict]:
    system_parts = [PERSONA_SYSTEM_PROMPT]
    now = datetime.now()
    system_parts.append(f"Data e hora atuais: {now:%A, %d/%m/%Y, %H:%M} (fuso local do usuario).")
    if profile_facts:
        system_parts.append(PROFILE_CONTEXT_TEMPLATE.format(facts=profile_facts))

    messages = [{"role": "system", "content": "\n\n".join(system_parts)}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})
    return messages
