# Ferramentas que o LLM pode chamar (function calling) para pesquisar na web,
# ler arquivos e usar a memoria de longo prazo - sem precisar que tudo isso
# va sempre no prompt.

from actions.browser import search_web_text
from actions.files import find_files, read_file, write_excel
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
]


def build_dispatch(profile: UserProfile, vector_store: VectorStore) -> dict:
    def _remember_fact(key: str, value: str) -> str:
        profile.remember(key, value)
        return f"Fato salvo: {key} = {value}."

    def _recall_memory(query: str) -> str:
        results = vector_store.search(query, top_k=3)
        return "\n".join(results) if results else "Nada relevante encontrado na memória."

    return {
        "web_search": lambda args: search_web_text(args["query"]),
        "read_file": lambda args: read_file(args["path"]),
        "find_files": lambda args: find_files(args["name"], args.get("root")),
        "create_excel": lambda args: write_excel(args["path"], args["rows"], args.get("headers")),
        "remember_fact": lambda args: _remember_fact(args["key"], args["value"]),
        "recall_memory": lambda args: _recall_memory(args["query"]),
    }
