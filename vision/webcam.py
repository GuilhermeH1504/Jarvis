# Modulo de visao computacional com OpenCV.

import cv2
import shutil
import tempfile
import threading
import time
from pathlib import Path


def load_face_cascade():
    cascade_name = "haarcascade_frontalface_default.xml"
    source_path = Path(cv2.data.haarcascades) / cascade_name

    if not source_path.exists():
        raise FileNotFoundError(f"[vision] Haar Cascade nao encontrado: {source_path}")

    path_to_load = source_path

    # No Windows, o OpenCV pode falhar ao abrir arquivos em caminhos com acento.
    if not str(source_path).isascii():
        safe_dir = Path(tempfile.gettempdir()) / "jarvis_opencv"
        safe_dir.mkdir(exist_ok=True)
        path_to_load = safe_dir / cascade_name
        shutil.copyfile(source_path, path_to_load)

    classifier = cv2.CascadeClassifier(str(path_to_load))
    if classifier.empty():
        raise RuntimeError(f"[vision] Nao consegui carregar o Haar Cascade: {path_to_load}")

    return classifier

class FaceWatcher:
    """
    Roda a webcam em uma thred separada, detectando rostos continuamente.
    Expoes uma flag 'face_detected' que o main.py pode checar a qualquer momento.
    """

    def __init__(self, camera_index: int=0, show_window: bool=True):
        self.camera_index = camera_index
        self.show_window = show_window
        self.face_detected = False
        self._running = False
        self._thread = None

        # Classificador pre-treinado do openCV para detecçao de rosto frontal
        self.face_cascade = load_face_cascade()


    def start(self):
        """Inicia a captura de webcam em backgrownd"""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Para a captura de webcam"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def _run(self):
        cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            print("[Vision] Nao consegui abrir a webcam. Verifique o indice da camera.")
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
                for (x,y,w,h) in faces:
                    cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
                    cv2.putText(frame, "JARVIS ONLINE", (x,y - 10)
                                , cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

                cv2.imshow("Jarvis - Visao", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self._running = False

        cap.release()
        if self.show_window:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    watcher = FaceWatcher(show_window=True)
    watcher.start()

    try:

        while True:
            time.sleep(0.5)
            print("Rosto detectado:", watcher.face_detected)
    except KeyboardInterrupt:
        watcher.stop()
