# Cliente de baixo nivel para a API da Groq (compativel com o formato da OpenAI,
# incluindo tool calling). Nao sabe nada sobre persona, historico ou memoria -
# isso fica por conta do resto do brain/.

from groq import AuthenticationError, Groq

from config import settings


class GroqLLM:
    def __init__(self, model: str | None = None):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in .env")

        self.model = model or settings.GROQ_MODEL
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def chat(self, messages: list[dict], tools: list[dict] | None = None, max_tokens: int = 600):
        """Manda a conversa pro modelo e devolve a mensagem de resposta (pode
        vir com .content preenchido ou com .tool_calls pra executar)."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None,
            )
        except AuthenticationError as exc:
            raise RuntimeError(
                "A Groq recusou sua API key. Gere uma nova chave no painel da Groq "
                "e coloque no .env como GROQ_API_KEY=gsk_..."
            ) from exc

        return response.choices[0].message


if __name__ == "__main__":

    llm = GroqLLM()
    print("Digite 'sair' pra encerrar.")
    history: list[dict] = []
    while True:
        msg = input("Voce: ")
        if msg.lower() == "sair":
            break
        history.append({"role": "user", "content": msg})
        reply = llm.chat(history).content
        history.append({"role": "assistant", "content": reply})
        print("Jarvis:", reply)
