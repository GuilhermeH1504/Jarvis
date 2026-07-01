# Modulo de integracao com a API da Claude.

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Você é o Jarvis, um assistente de IA pessoal estilo Tony Stark.
Seja direto, levemente sarcástico, mas sempre útil. Respostas curtas e objetivas,
porque suas respostas serão faladas em voz alta - evite listas longas ou markdown.
Fale em português do Brasil."""

class JarvisBrain:
    def __init__(self, model: str = "openai/gpt-oss-120b", max_history: int = 10):
        self.model = model
        self.max_history = max_history

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env")