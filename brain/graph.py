# Orquestrador principal do Jarvis: decide entre comando de sistema direto
# (via router.py, sem custo de LLM) e conversa com o LLM (que pode usar as
# tools de brain/tools.py). E' o que main.py importa como JarvisBrain.

import json

from actions import apps, system
from brain.groq_agent import GroqLLM
from brain.prompt import build_messages
from brain.router import Intent, route
from brain.tools import TOOL_SCHEMAS, build_dispatch
from memory.history import ConversationHistory
from memory.profile import UserProfile
from memory.vector_store import VectorStore

_LOCAL_ACTIONS = {
    "open_app": lambda args, _confirm: apps.open_app(args["value"]),
    "lock": lambda _args, _confirm: system.lock(),
    "shutdown": lambda _args, confirm: system.shutdown(confirm=confirm),
    "restart": lambda _args, confirm: system.restart(confirm=confirm),
}
_CONFIRMABLE = {"shutdown", "restart"}
_CONFIRM_WORDS = {"sim", "confirmo", "confirmar", "pode", "isso"}
_MAX_TOOL_ROUNDS = 4


class JarvisBrain:
    def __init__(self):
        self.llm = GroqLLM()
        self.history = ConversationHistory()
        self.profile = UserProfile()
        self.vector_store = VectorStore()
        self.tool_dispatch = build_dispatch(self.profile, self.vector_store)
        self._pending_action: Intent | None = None

    def think(self, user_input: str) -> str:
        if self._pending_action is not None:
            pending = self._pending_action
            self._pending_action = None
            if user_input.strip().lower() in _CONFIRM_WORDS:
                return self._run_local_action(pending, confirm=True)
            return self._handle_chat(user_input)

        intent = route(user_input)
        if intent.kind == "action":
            return self._run_local_action(intent, confirm=False)
        return self._handle_chat(user_input)

    def _run_local_action(self, intent: Intent, confirm: bool) -> str:
        handler = _LOCAL_ACTIONS.get(intent.action)
        if not handler:
            return "Não sei executar essa ação ainda."

        response = handler(intent.args, confirm)

        if intent.action in _CONFIRMABLE and not confirm:
            self._pending_action = intent

        self.history.add("user", intent.action)
        self.history.add("assistant", response)
        return response

    def _handle_chat(self, user_input: str) -> str:
        messages = build_messages(
            history=self.history.recent(),
            user_input=user_input,
            profile_facts=self.profile.as_context_string(),
        )

        reply = "Deu muitas voltas tentando resolver isso, pode reformular a pergunta?"
        for _ in range(_MAX_TOOL_ROUNDS):
            message = self.llm.chat(messages, tools=TOOL_SCHEMAS)

            if not message.tool_calls:
                reply = message.content or ""
                break

            messages.append(message.model_dump(exclude_none=True))
            for call in message.tool_calls:
                result = self._execute_tool(call.function.name, call.function.arguments)
                messages.append(
                    {"role": "tool", "tool_call_id": call.id, "content": result}
                )

        self.history.add("user", user_input)
        self.history.add("assistant", reply)
        self.vector_store.add(f"Usuário perguntou: {user_input}\nJarvis respondeu: {reply}")
        return reply

    def _execute_tool(self, name: str, raw_arguments: str) -> str:
        handler = self.tool_dispatch.get(name)
        if not handler:
            return f"Ferramenta '{name}' não existe."

        try:
            args = json.loads(raw_arguments) if raw_arguments else {}
            return handler(args)
        except Exception as exc:
            return f"Erro ao executar '{name}': {exc}"
