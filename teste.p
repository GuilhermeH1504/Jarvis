"""
vision/webcam.py
Responsável por ligar a webcam e detectar rosto usando Haar Cascade (OpenCV).
Quando detecta um rosto, sinaliza que o Jarvis pode "acordar" e ouvir comandos.
"""

import cv2
import threading
import time


class FaceWatcher:
    """
    Roda a webcam em uma thread separada, detectando rostos continuamente.
    Expõe uma flag `face_detected` que o main.py pode checar a qualquer momento.
    """

    def __init__(self, camera_index: int = 0, show_window: bool = True):
        self.camera_index = camera_index
        self.show_window = show_window
        self.face_detected = False
        self._running = False
        self._thread = None

        # Classificador pré-treinado do OpenCV pra detecção de rosto frontal
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def start(self):
        """Inicia a captura da webcam em background."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Para a captura da webcam."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            print("[vision] Não consegui abrir a webcam. Verifique o índice da câmera.")
            self._running = False
            return

        while self._running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
            )

            self.face_detected = len(faces) > 0

            if self.show_window:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(
                        frame, "JARVIS ONLINE", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
                    )

                cv2.imshow("Jarvis - Visao", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self._running = False

        cap.release()
        if self.show_window:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    # Teste isolado: roda só a visão, sem o resto do Jarvis
    watcher = FaceWatcher(show_window=True)
    watcher.start()

    try:
        while True:
            time.sleep(0.5)
            print("Rosto detectado:" , watcher.face_detected)
    except KeyboardInterrupt:
        watcher.stop()