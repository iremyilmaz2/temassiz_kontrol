import cv2
import mediapipe as mp
import numpy as np
from keras.models import load_model
import pickle

# MediaPipe kurulumu
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, 
                        min_detection_confidence=0.7)

# Model ve hareket isimlerini yükle
print("Model yükleniyor...")
model = load_model('el_hareket_modeli.h5')

with open('hareket_isimleri.pkl', 'rb') as f:
    hareketler = pickle.load(f)

print("✓ Model yüklendi!")
print(f"Tanınabilecek hareketler: {', '.join(hareketler)}")

def test_realtime():
    cap = cv2.VideoCapture(0)
    
    print("\nGerçek zamanlı test başladı!")
    print("Çıkmak için 'q' tuşuna basın.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # El çiz
                mp_draw.draw_landmarks(frame, hand_landmarks, 
                                      mp_hands.HAND_CONNECTIONS)
                
                # Landmark'ları al
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.extend([lm.x, lm.y, lm.z])
                
                # Tahmin yap
                landmarks = np.array(landmarks).reshape(1, -1)
                tahmin = model.predict(landmarks, verbose=0)
                hareket_idx = np.argmax(tahmin)
                guven = tahmin[0][hareket_idx]
                
                # Sonucu göster
                hareket_adi = hareketler[hareket_idx]
                
                # Güven %70'in üzerindeyse göster
                if guven > 0.7:
                    cv2.putText(frame, f"{hareket_adi}", (10, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    cv2.putText(frame, f"Guven: {guven*100:.1f}%", (10, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "Belirsiz", (10, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        else:
            cv2.putText(frame, "El bulunamadi", (10, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow('El Hareket Tanima - Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_realtime()