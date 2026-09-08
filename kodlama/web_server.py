import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import cv2
import mediapipe as mp
import numpy as np
from keras.models import load_model
import pickle
from flask import Flask
from flask_socketio import SocketIO
import base64
import pyautogui
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Model ve Etiket Yükleme
try:
    model = load_model('el_hareket_modeli.h5')
    with open('hareket_isimleri.pkl', 'rb') as f:
        hareketler = pickle.load(f)
    print(">>> SİSTEM HAZIR: Hareketleri algılamaya başlayabilirsiniz.")
except Exception as e:
    print(f">>> HATA: Dosyalar yüklenemedi: {e}")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.8)

son_islem_zamani = 0
BEKLEME_SURESI = 3.0 

@socketio.on("process_frame")
def process_frame(data):
    global son_islem_zamani
    try:
        simdi = time.time()
        if simdi - son_islem_zamani < BEKLEME_SURESI:
            return

        image_data = data["image"]
        # React'tan gelen mapping objesini al (Hepsi küçük harf anahtarlı gelmeli)
        user_mapping = data.get("user_mapping", {})
        
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None: return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.extend([lm.x, lm.y, lm.z])

                input_data = np.array(landmarks).reshape(1, -1)
                tahmin = model.predict(input_data, verbose=0)
                idx = np.argmax(tahmin)
                guven = tahmin[0][idx]

                if guven > 0.85:
                    # Modelden gelen ham ismi temizle ve küçük harf yap
                    ham_tespit = str(hareketler[idx]).lower().strip()
                    
                    # Eşleşme var mı bak, yoksa ham ismi kullan
                    secilen_komut = user_mapping.get(ham_tespit, ham_tespit)
                    
                    son_islem_zamani = simdi
                    execute_command(secilen_komut)
                    socketio.emit("gesture_command", {"command": secilen_komut})
                    print(f"Model: {ham_tespit} | Atanan Komut: {secilen_komut}")

    except Exception as e:
        print(f"Hata: {e}")

def execute_command(komut):
    k = str(komut).lower().strip()
    if k in ["duraklat", "oynat"]: pyautogui.press('space')
    elif k == "ses_ac": pyautogui.press('volumeup')
    elif k == "ses_kapat": pyautogui.press('volumedown')
    elif k == "tam_ekran": pyautogui.press('f')
    elif k == "kucuk_ekran": pyautogui.press('i')
    elif k == "sonraki_video": pyautogui.hotkey('shift', 'n')
    elif k == "onceki_video": pyautogui.hotkey('shift', 'p')
    elif k == "video_geri": pyautogui.press('l')
    elif k == "video_ileri": pyautogui.press('j')
    elif k == "ekran_goruntusu": pyautogui.hotkey('win', 'printscreen')

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)