# Acoes de navegador: abrir sites/pesquisas visualmente, e pesquisa de texto
# (DuckDuckGo, sem precisar de API key) que o LLM usa como tool pra ler
# resultados sem precisar abrir nada na tela.

import urllib.parse
import webbrowser

from ddgs import DDGS


def open_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    webbrowser.open(url)
    return f"Abrindo {url}."


def search_web(query: str) -> str:
    search_url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
    webbrowser.open(search_url)
    return f"Pesquisando '{query}' no Google."


def search_web_text(query: str, max_results: int = 5) -> str:
    """Pesquisa e devolve titulo/resumo/link em texto, pra o LLM ler - nao abre
    nada na tela. Usa DuckDuckGo por nao exigir API key."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as exc:
        return f"Não consegui pesquisar agora: {exc}"

    if not results:
        return "Nenhum resultado encontrado."

    lines = [
        f"- {item.get('title', '')}: {item.get('body', '')} ({item.get('href', '')})"
        for item in results
    ]
    return "\n".join(lines)
