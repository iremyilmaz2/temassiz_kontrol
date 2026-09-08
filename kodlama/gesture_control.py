import cv2
import mediapipe as mp
import numpy as np
from keras.models import load_model
import pickle
import pyautogui
import time
import os

# 1. Model ve Etiketleri Yükle
model_yolu = 'el_hareket_modeli.h5'
isimler_yolu = 'hareket_isimleri.pkl'

print("Sistem yükleniyor...")
model = load_model(model_yolu)
with open(isimler_yolu, 'rb') as f:
    hareketler = pickle.load(f)

# 2. MediaPipe Kurulumu
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)

# 3. Kamera Başlatma
cap = cv2.VideoCapture(0)

# --- ZAMANLAMA AYARLARI ---
son_islem_zamani = 0
bekleme_suresi = 3.0  # Bir komuttan sonra diğerine geçmek için 3 saniye bekle
# --------------------------

print(f"\n✓ SİSTEM AKTİF! Komutlar arası bekleme süresi: {bekleme_suresi} saniye.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    simdi = time.time()
    kalan_sure = max(0, int(bekleme_suresi - (simdi - son_islem_zamani)))

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            
            input_data = np.array(landmarks).reshape(1, -1)
            tahmin = model.predict(input_data, verbose=0)
            hareket_idx = np.argmax(tahmin)
            guven = tahmin[0][hareket_idx]
            hareket_adi = hareketler[hareket_idx]
            
            if guven > 0.85:
                # EKRAN BİLGİSİ: Eğer bekleme süresi dolmadıysa kırmızı, dolduysa yeşil göster
                if kalan_sure > 0:
                    cv2.putText(frame, f"BEKLEYIN: {kalan_sure}s", (10, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, f"HAZIR: {hareket_adi}", (10, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                    # KOMUT GÖNDERME (Sadece süre dolduysa)
                    print(f"KOMUT TETİKLENDİ: {hareket_adi}")
                    
                    if hareket_adi in ["duraklat", "oynat"]:
                        pyautogui.press('space')
                    elif hareket_adi == "ses_ac":
                        pyautogui.press('volumeup')
                    elif hareket_adi == "ses_kapat":
                        pyautogui.press('volumedown')
                    elif hareket_adi == "tam_ekran":
                        pyautogui.press('f')
                    elif hareket_adi == "kucuk_ekran":
                        pyautogui.press('esc')
                    elif hareket_adi == "video_ileri":
                        pyautogui.press('right')
                    elif hareket_adi == "video_geri":
                        pyautogui.press('left')
                    elif hareket_adi == "sonraki_video":
                        pyautogui.hotkey('shift', 'n')
                    elif hareket_adi == "onceki_video":
                        pyautogui.hotkey('shift', 'p')
                    elif hareket_adi == "ekran_goruntusu":
                        pyautogui.press('printscreen')
                    
                    son_islem_zamani = simdi # Zamanı güncelle
            else:
                cv2.putText(frame, "Analiz ediliyor...", (10, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

    cv2.imshow('El Kontrol Paneli', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()