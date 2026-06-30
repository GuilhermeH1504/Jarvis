"""
audio/stt.py
Responsável por gravar áudio do microfone e transcrever usando Whisper (local, sem API paga).
"""

import sounddevice as sd
import numpy as np
import whisper
import tempfile
import scipy.io.wavfile as wavfile


class SpeechToText:
    def __init__(self, model_size: str = "base", sample_rate: int = 16000):
        """
        model_size: tiny, base, small, medium, large
                    'base' é um bom equilíbrio entre velocidade e precisão pra começar.
        """
        print(f"[stt] Carregando modelo Whisper '{model_size}'... (só na primeira vez baixa)")
        self.model = whisper.load_model(model_size)
        self.sample_rate = sample_rate

    def record(self, duration: int = 5) -> np.ndarray:
        """Grava áudio do microfone por `duration` segundos."""
        print(f"[stt] 🎙️  Gravando por {duration}s... fale agora.")
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        print("[stt] Gravação finalizada.")
        return audio.flatten()

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcreve um array de áudio em texto usando Whisper."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            wavfile.write(tmp.name, self.sample_rate, audio)
            result = self.model.transcribe(tmp.name, language="pt")
            return result["text"].strip()

    def listen(self, duration: int = 5) -> str:
        """Grava e já retorna o texto transcrito. Atalho pro uso comum."""
        audio = self.record(duration)
        text = self.transcribe(audio)
        print(f"[stt] Você disse: {text}")
        return text


if __name__ == "__main__":
    # Teste isolado: grava 5s e mostra a transcrição
    stt = SpeechToText(model_size="base")
    texto = stt.listen(duration=5)
    print("Transcrição final:", texto)