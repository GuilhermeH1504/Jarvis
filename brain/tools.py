# Ferramentas que o LLM pode chamar (function calling) para pesquisar na web,
# ler arquivos e usar a memoria de longo prazo - sem precisar que tudo isso
# va sempre no prompt.

from datetime import datetime, timedelta

from actions.browser import search_web_text
from actions.files import find_files, read_file, write_excel
from actions.reminders import ReminderStore
from memory.profile import UserProfile
from memory.vector_store import VectorStore

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Pesquisa na web e retorna titulo, resumo e link dos resultados mais relevantes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "O que pesquisar."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Le o conteudo de um arquivo de texto no computador do usuario para analise.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho do arquivo a ser lido."},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_files",
            "description": "Procura arquivos pelo nome nas pastas comuns do usuario (Area de Trabalho, Documentos, Downloads, Imagens, Videos, Musica, OneDrive). Use antes de create_excel se o usuario mencionar um arquivo que ja deve existir, pra achar o caminho certo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome ou parte do nome do arquivo a procurar."},
                    "root": {
                        "type": "string",
                        "description": "Pasta especifica para buscar, se o usuario indicar um local fora das pastas padrao (ex: 'D:/Projetos'). Deixe vazio pra usar as pastas padrao.",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_excel",
            "description": "Cria uma planilha Excel (.xlsx) com os dados fornecidos. Se o caminho apontar pra um arquivo que ja existe, adiciona as linhas nele em vez de sobrescrever.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Nome ou caminho do arquivo, ex: 'gastos.xlsx'. Se for so o nome, salva na Area de Trabalho.",
                    },
                    "headers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Cabecalho das colunas (opcional).",
                    },
                    "rows": {
                        "type": "array",
                        "items": {"type": "array", "items": {}},
                        "description": "Linhas de dados; cada linha e uma lista com o valor de cada coluna.",
                    },
                },
                "required": ["path", "rows"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember_fact",
            "description": "Guarda um fato importante e permanente sobre o usuario para lembrar em conversas futuras.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Nome curto do fato, ex: 'time_favorito'."},
                    "value": {"type": "string", "description": "O valor do fato."},
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memory",
            "description": "Busca na memoria de longo prazo trechos de conversas antigas relacionados a um assunto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Assunto a buscar na memoria."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_reminder",
            "description": "Cria um lembrete que o Jarvis vai avisar na hora certa. Informe OU 'in_minutes' (para 'daqui a 10 minutos') OU 'at' (para horario especifico, ex: 'amanha as 9h'), usando a data e hora atuais do prompt como referencia.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "O que deve ser lembrado, ex: 'tomar remedio'."},
                    "in_minutes": {"type": "integer", "description": "Daqui a quantos minutos avisar."},
                    "at": {"type": "string", "description": "Data e hora no formato ISO, ex: '2026-09-22T09:00:00'."},
                },
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_reminders",
            "description": "Lista os lembretes pendentes do usuario, com id e horario.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_reminder",
            "description": "Cancela um lembrete pendente pelo id. Use list_reminders antes para achar o id certo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reminder_id": {"type": "string", "description": "Id do lembrete a cancelar."},
                },
                "required": ["reminder_id"],
            },
        },
    },
]


def build_dispatch(profile: UserProfile, vector_store: VectorStore, reminders: ReminderStore) -> dict:
    def _remember_fact(key: str, value: str) -> str:
        profile.remember(key, value)
        return f"Fato salvo: {key} = {value}."

    def _recall_memory(query: str) -> str:
        results = vector_store.search(query, top_k=3)
        return "\n".join(results) if results else "Nada relevante encontrado na memória."

    def _create_reminder(message: str, in_minutes: int | None = None, at: str | None = None) -> str:
        if in_minutes is not None:
            due = datetime.now() + timedelta(minutes=in_minutes)
        elif at:
            try:
                due = datetime.fromisoformat(at)
            except ValueError:
                return f"Horário inválido: '{at}'. Use o formato 2026-09-22T09:00:00."
        else:
            return "Preciso saber quando avisar: informe 'in_minutes' ou 'at'."

        if due <= datetime.now():
            return "Esse horário já passou. Peça um horário no futuro."

        reminder = reminders.add(message, due)
        return f"Lembrete criado (id {reminder['id']}): '{message}' em {due:%d/%m/%Y às %H:%M}."

    def _list_reminders() -> str:
        pending = reminders.list_pending()
        if not pending:
            return "Você não tem lembretes pendentes."
        return "\n".join(
            f"- [{r['id']}] {r['message']} ({datetime.fromisoformat(r['due']):%d/%m às %H:%M})"
            for r in pending
        )

    def _cancel_reminder(reminder_id: str) -> str:
        if reminders.cancel(reminder_id):
            return f"Lembrete {reminder_id} cancelado."
        return f"Não encontrei um lembrete com o id '{reminder_id}'."

    return {
        "web_search": lambda args: search_web_text(args["query"]),
        "read_file": lambda args: read_file(args["path"]),
        "find_files": lambda args: find_files(args["name"], args.get("root")),
        "create_excel": lambda args: write_excel(args["path"], args["rows"], args.get("headers")),
        "remember_fact": lambda args: _remember_fact(args["key"], args["value"]),
        "recall_memory": lambda args: _recall_memory(args["query"]),
        "create_reminder": lambda args: _create_reminder(
            args["message"], args.get("in_minutes"), args.get("at")
        ),
        "list_reminders": lambda args: _list_reminders(),
        "cancel_reminder": lambda args: _cancel_reminder(args["reminder_id"]),
    }
