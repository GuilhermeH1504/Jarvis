# Modulo de reconhecimento de voz com Whisper.

import sounddevice as sd
import numpy as np
import whisper
import tempfile 
import scipy.io.wavfile as wavfile

class SpeechToText:
    def __init__(self, model_size: str = 'base', sample_rate: int = 16000):
        """ 
        model_size: tiny,base,small,medium, large
                        'base' e um bom equilibrio entre velocidade e precisao

        """
        print(f"[stt] Carregando modelo Whisper '{model_size}'... (so na primeira vez baixa)")
        self.model = whisper.load_model(model_size)
        self.sample_rate = sample_rate

    def record(self, duration: int = 5)-> np.ndarray:
        """ 
        Grava audio do microfone por 'duration' segundos
        """
        print(f"[stt] Gravando por '{duration}' segundos...")
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
        )
        sd.wait()
        return audio.flatten()
    
    def transcribe(self, audio: np.ndarray)-> str:
        """Transcreve um array de audio em texto"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as tmp:
            wavfile.write(tmp.name, self.sample_rate, audio)
            result = self.model.transcribe(tmp.name, language='pt')
            return result['text'].strip()

    def listen(self, duration: int=5):
        """Grava e ja retorna o texto transcrito. Atalho pro uso comum."""
        audio = self.record(duration)
        text = self.transcribe(audio)
        print(f"[stt] Você disse: {text}")
        return text
        

if __name__ ==  "__main__":
    stt = SpeechToText(model_size='base')
    texto = stt.listen(duration=5)
    print("Transcricao:", texto)