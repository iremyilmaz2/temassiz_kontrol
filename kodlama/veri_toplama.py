import cv2
import mediapipe as mp
import numpy as np
import os
import time

# MediaPipe kurulumu
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, 
                        min_detection_confidence=0.7)

# Hareketler
hareketler = ["duraklat", "oynat", "ses_ac", "ses_kapat", "onceki_video", 
              "sonraki_video", "video_ileri", "video_geri", "tam_ekran", 
              "kucuk_ekran", "ekran_goruntusu"]

def veri_topla():
    # Veri klasörü oluştur
    if not os.path.exists('veri'):
        os.makedirs('veri')
    
    cap = cv2.VideoCapture(0)
    
    for hareket in hareketler:
        print(f"\n{hareket.upper()} hareketi için hazırlanın!")
        print("5 saniye sonra başlayacak...")
        
        for i in range(5, 0, -1):
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            cv2.putText(frame, f"{hareket} - {i}", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            cv2.imshow('Veri Toplama', frame)
            cv2.waitKey(1000)
        
        # Her hareket için veri toplama
        hareket_verileri = []
        foto_sayisi = 150  # Her hareket için 150 fotoğraf
        
        print(f"{hareket} için {foto_sayisi} fotoğraf çekiliyor...")
        
        for i in range(foto_sayisi):
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # El noktalarını çiz
                    mp_draw.draw_landmarks(frame, hand_landmarks, 
                                          mp_hands.HAND_CONNECTIONS)
                    
                    # Landmark'ları kaydet (21 nokta x 3 koordinat = 63 özellik)
                    landmarks = []
                    for lm in hand_landmarks.landmark:
                        landmarks.extend([lm.x, lm.y, lm.z])
                    
                    hareket_verileri.append(landmarks)
            
            # İlerleme göster
            cv2.putText(frame, f"{hareket}: {i+1}/{foto_sayisi}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Veri Toplama', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Veriyi kaydet
        if len(hareket_verileri) > 0:
            np.save(f'veri/{hareket}.npy', np.array(hareket_verileri))
            print(f"{hareket} için {len(hareket_verileri)} veri kaydedildi.")
        else:
            print(f"UYARI: {hareket} için veri toplanamadı!")
        
        print("\n5 saniye ara...")
        time.sleep(5)
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n✓ Tüm veriler toplandı!")

if __name__ == "__main__":
    veri_topla()