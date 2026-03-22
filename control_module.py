import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import asyncio
import websockets
import time
import os
import requests

# ----------- 📥 Téléchargement automatique du modèle -----------
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = "hand_landmarker.task"

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("📥 Téléchargement du modèle...")
        response = requests.get(MODEL_URL)
        response.raise_for_status()

        with open(MODEL_PATH, "wb") as f:
            f.write(response.content)

        print("✅ Modèle téléchargé !")


# ----------- 🎮 CV Controller -----------
class CVController:
    def __init__(self, screen_width=640, screen_height=480):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Anti-spam
        self.last_command_time = 0
        self.cooldown = 0.4

        # Télécharger le modèle si nécessaire
        download_model()

        # MediaPipe
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            running_mode=vision.RunningMode.IMAGE
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

        # Webcam
        self.cap = cv2.VideoCapture(0)

    def get_command(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.landmarker.detect(mp_image)

        command = None

        if result.hand_landmarks:
            hand = result.hand_landmarks[0]

            wrist = hand[0]
            thumb_tip = hand[4]
            index_tip = hand[8]
            middle_tip = hand[12]
            ring_tip = hand[16]
            pinky_tip = hand[20]

            # ----------- 🎮 ENTER (main ouverte) -----------
            if (
                thumb_tip.y < wrist.y and
                index_tip.y < wrist.y and
                middle_tip.y < wrist.y and
                ring_tip.y < wrist.y and
                pinky_tip.y < wrist.y
            ):
                command = "ENTER"

            # ----------- 🔥 FIRE (2 doigts levés) -----------
            elif (
                index_tip.y < wrist.y - 0.1 and
                middle_tip.y < wrist.y - 0.1
            ):
                command = "FIRE"

            # ----------- ⬅️➡️ MOUVEMENT -----------
            else:
                wrist_x = wrist.x * self.screen_width

                if wrist_x < self.screen_width * 0.4:
                    command = "LEFT"
                elif wrist_x > self.screen_width * 0.6:
                    command = "RIGHT"

            # Dessin des points (debug)
            for lm in hand:
                x = int(lm.x * self.screen_width)
                y = int(lm.y * self.screen_height)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

        # ----------- ⏱️ Anti-spam -----------
        current_time = time.time()
        if command and (current_time - self.last_command_time > self.cooldown):
            self.last_command_time = current_time
            print("Commande détectée:", command)
        else:
            command = None

        # ----------- 🛑 QUIT clavier -----------
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):  # ESC ou Q
            return "QUIT"

        # Affichage
        cv2.putText(frame, "ESC ou Q pour quitter", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("CV Controller", frame)

        return command

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()


# ----------- 🌐 WebSocket -----------
async def main():
    uri = "ws://localhost:8765"
    controller = CVController()

    async with websockets.connect(uri) as websocket:
        print("✅ Connecté au serveur Space Invaders")

        try:
            while True:
                cmd = controller.get_command()

                if cmd == "QUIT":
                    print("🛑 Fermeture du jeu")
                    break

                if cmd:
                    await websocket.send(cmd)
                    print("Envoyé:", cmd)

                await asyncio.sleep(0.05)

        except KeyboardInterrupt:
            print("🛑 Arrêt manuel")

        finally:
            controller.release()


if __name__ == "__main__":
    asyncio.run(main())