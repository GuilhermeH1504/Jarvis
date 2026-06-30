# Modulo de sintese de voz com gTTS ou pyttsx3.

import pyttsx3

class TextSpeech:
    def __init__(self, rate: int=75, volume: float=1.0, voice_index: int=0):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)

        voices = self.engine.getProperty("voices")
        if voices and voice_index < len(voices):
            self.engine.setProperty("voice", voices[voice_index].id)

    def speak(self, text: str):
        """Fala o texto em voz alta (bloqueia ate terminar de falar)"""
        print(f"[tts] Jarvis: {text}")
        self.engine.say(text)
        self.engine.runAndWait()


    def list_voices(self):
        """Lista as voxes disponiveis no sistema, util pra escolher a melhor em PT-BR"""
        voices = self.engine.getProperty("voices")
        for i,v in enumerate(voices):
            print(f"{i}: {v.name}")

if __name__ == "__main__":
    tts = TextSpeech()
    print("Vozes disponiveis no seu sistema:")
    tts.list_voices()
    tts.speak("Ola, tudo bem?. Como posso ajudar?")