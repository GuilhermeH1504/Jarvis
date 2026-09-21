# Orquestrador principal do Jarvis.

import argparse
import queue
import time

WAKE_PHRASES_TO_EXIT = {"sair", "encerrar", "tchau jarvis", "desligar"}


def run_text_mode():
    from actions.reminders import ReminderWatcher
    from brain.graph import JarvisBrain

    print("=" * 50)
    print(" JARVIS - MODO TEXTO ")
    print("=" * 50)
    print("Digite 'sair' para encerrar.\n")

    brain = JarvisBrain()

    # O print reescreve o "Voce: " no fim porque o input() continua esperando.
    watcher = ReminderWatcher(
        brain.reminders,
        on_due=lambda r: print(f"\n[Lembrete] {r['message']}\nVoce: ", end="", flush=True),
    )
    watcher.start()

    try:
        while True:
            user_text = input("Voce: ").strip()
            if not user_text:
                continue
            if user_text.lower() in WAKE_PHRASES_TO_EXIT:
                print("Jarvis: Tchau, volte sempre!")
                break

            resposta = brain.think(user_text)
            print(f"Jarvis: {resposta}\n")
    finally:
        watcher.stop()


def run_voice_mode():
    from actions.reminders import ReminderWatcher
    from vision.webcam import FaceWatcher
    from audio.stt import SpeechToText
    from audio.tts import TextSpeech
    from brain.graph import JarvisBrain

    print("=" * 50)
    print(" INICIALIZANDO JARVIS - MODO VOZ ")
    print("=" * 50)

    print("\n[1/4] Carregando visao computacional...")
    watcher = FaceWatcher(show_window=True)
    watcher.start()

    print("\n[2/4] Carregando reconhecimento de voz...")
    stt = SpeechToText(model_size="base")

    print("\n[3/4] Carregando sintetizador de voz...")
    tts = TextSpeech()

    print("\n[4/4] Carregando inteligencia artificial...")
    brain = JarvisBrain()

    # A thread do watcher so enfileira; quem fala e o loop principal, porque o
    # pyttsx3 nao deve ser usado de duas threads ao mesmo tempo.
    due_messages = queue.Queue()
    reminder_watcher = ReminderWatcher(
        brain.reminders, on_due=lambda r: due_messages.put(r["message"])
    )
    reminder_watcher.start()

    print("\nJarvis iniciado em modo voz.")
    print("Olhe para a webcam e fale quando ele disser que esta ouvindo.")
    print("Para encerrar, fale 'sair' ou aperte Ctrl+C.\n")

    try:
        while True:
            while not due_messages.empty():
                tts.speak(f"Lembrete: {due_messages.get()}")

            if watcher.face_detected:
                tts.speak("Pode falar, estou te ouvindo.")
                user_text = stt.listen(duration=5)

                if not user_text:
                    continue
                if user_text.lower().strip() in WAKE_PHRASES_TO_EXIT:
                    tts.speak("Tchau, volte sempre!")
                    break

                resposta = brain.think(user_text)
                tts.speak(resposta)

                time.sleep(1)
            else:
                time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[main] Interrompido pelo usuario")
    finally:
        watcher.stop()
        reminder_watcher.stop()
        print("=" * 50)
        print("[main] Encerrando Jarvis...")


def choose_mode():
    print("=" * 50)
    print(" JARVIS ")
    print("=" * 50)
    print("[1] Modo texto")
    print("[2] Modo voz com webcam e microfone")

    while True:
        choice = input("\nEscolha o modo: ").strip()
        if choice == "1":
            return "texto"
        if choice == "2":
            return "voz"
        print("Opcao invalida. Digite 1 ou 2.")


def main():
    parser = argparse.ArgumentParser(description="Jarvis")
    parser.add_argument(
        "--modo",
        choices=["texto", "voz"],
        help="Escolhe o modo sem abrir o menu inicial.",
    )
    args = parser.parse_args()

    mode = args.modo or choose_mode()
    if mode == "texto":
        run_text_mode()
    else:
        run_voice_mode()


if __name__ == "__main__":
    main()
