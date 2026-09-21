# Configuracao central do Jarvis: variaveis de ambiente e caminhos de dados.

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


def _clean_env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip().strip('"').strip("'")


GROQ_API_KEY = _clean_env("GROQ_API_KEY")
GROQ_MODEL = _clean_env("GROQ_MODEL", "openai/gpt-oss-120b")

# Poucos turnos ficam no historico "cru" enviado a cada mensagem; conversas
# mais antigas viram memoria de longo prazo (vector_store) e so voltam ao
# contexto quando o proprio modelo pede via tool call, pra nao gastar tokens
# a toa em toda mensagem.
MAX_HISTORY_TURNS = int(_clean_env("JARVIS_MAX_HISTORY_TURNS", "3") or 3)

HISTORY_FILE = DATA_DIR / "history.json"
PROFILE_FILE = DATA_DIR / "profile.json"
VECTOR_STORE_FILE = DATA_DIR / "vector_store.json"
