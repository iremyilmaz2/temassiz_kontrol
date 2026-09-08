import numpy as np
import os
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.utils import to_categorical
import pickle
import cv2
import mediapipe as mp
from glob import glob

# MediaPipe kurulumu
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, 
                        min_detection_confidence=0.5)

# Hareketler
hareketler = ["duraklat", "oynat", "ses_ac", "ses_kapat", "onceki_video", 
              "sonraki_video", "video_ileri", "video_geri", "tam_ekran", 
              "kucuk_ekran", "ekran_goruntusu"]

def goruntuyu_isle_ve_landmark_cikart(img):
    """Görüntüden el landmark'larını çıkart"""
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            return landmarks
    return None

def hazir_datasetten_veri_yukle(dataset_klasoru='veri'):
    """
    Hazır dataset klasöründen fotoğrafları yükle ve landmark'lara çevir
    
    Klasör yapısı:
    veri/
      ├── duraklat/
      │   ├── foto1.jpg
      │   ├── foto2.jpg
      │   └── ...
      ├── oynat/
      │   └── ...
      └── ...
    """
    X = []  # Özellikler (landmarks)
    y = []  # Etiketler
    
    print("Hazır datasetten veriler yükleniyor ve işleniyor...")
    print("=" * 60)
    
    for idx, hareket in enumerate(hareketler):
        hareket_klasoru = os.path.join(dataset_klasoru, hareket)
        
        if not os.path.exists(hareket_klasoru):
            print(f"⚠️  UYARI: {hareket_klasoru} klasörü bulunamadı! Atlanıyor...")
            continue
        
        # Tüm fotoğrafları bul
        foto_yollari = glob(os.path.join(hareket_klasoru, "*.jpg")) + \
                       glob(os.path.join(hareket_klasoru, "*.png")) + \
                       glob(os.path.join(hareket_klasoru, "*.jpeg"))
        
        if len(foto_yollari) == 0:
            print(f"⚠️  UYARI: {hareket} klasöründe fotoğraf bulunamadı!")
            continue
        
        print(f"\n📁 {hareket.upper()}")
        print(f"   Bulunan fotoğraf: {len(foto_yollari)}")
        
        basarili = 0
        basarisiz = 0
        
        for foto_yol in foto_yollari:
            img = cv2.imread(foto_yol)
            
            if img is None:
                basarisiz += 1
                continue
            
            # Landmark çıkart
            landmarks = goruntuyu_isle_ve_landmark_cikart(img)
            
            if landmarks is not None:
                X.append(landmarks)
                y.append(idx)
                basarili += 1
            else:
                basarisiz += 1
        
        print(f"   ✅ Başarılı: {basarili}")
        print(f"   ❌ Başarısız: {basarisiz}")
        print(f"   📊 Başarı oranı: {(basarili/(basarili+basarisiz)*100):.1f}%")
    
    return np.array(X), np.array(y)

def model_egit(dataset_klasoru='veri'):
    """
    Hazır datasetten model eğit
    
    Args:
        dataset_klasoru: Fotoğrafların bulunduğu ana klasör (varsayılan: 'veri')
    """
    
    # Verileri yükle
    X, y = hazir_datasetten_veri_yukle(dataset_klasoru)
    
    if len(X) == 0:
        print("\n❌ HATA: Hiç veri yüklenemedi!")
        print("Lütfen klasör yapısını kontrol edin:")
        print(f"{dataset_klasoru}/")
        print("  ├── duraklat/")
        print("  │   ├── foto1.jpg")
        print("  │   └── ...")
        print("  ├── oynat/")
        print("  └── ...")
        return
    
    print("\n" + "=" * 60)
    print(f"TOPLAM VERİ: {len(X)} örnek, {len(hareketler)} sınıf")
    print("=" * 60)
    
    # Sınıf dağılımını göster
    print("\n📊 Sınıf Dağılımı:")
    for idx, hareket in enumerate(hareketler):
        sayi = np.sum(y == idx)
        print(f"   {hareket}: {sayi} örnek")
    
    # Veriyi böl
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📦 Eğitim seti: {len(X_train)} örnek")
    print(f"📦 Test seti: {len(X_test)} örnek")
    
    # One-hot encoding
    y_train = to_categorical(y_train, num_classes=len(hareketler))
    y_test = to_categorical(y_test, num_classes=len(hareketler))
    
    # Model oluştur
    print("\n🔧 Model oluşturuluyor...")
    model = Sequential([
        Dense(128, activation='relu', input_shape=(63,)),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dense(len(hareketler), activation='softmax')
    ])
    
    model.compile(optimizer='adam', 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])
    
    print(model.summary())
    
    # Modeli eğit
    print("\n🚀 Model eğitiliyor...")
    print("=" * 60)
    history = model.fit(X_train, y_train, 
                       validation_data=(X_test, y_test),
                       epochs=50, 
                       batch_size=32,
                       verbose=1)
    
    # Modeli kaydet
    print("\n" + "=" * 60)
    model.save('el_hareket_modeli.h5')
    print("✅ Model 'el_hareket_modeli.h5' olarak kaydedildi!")
    
    # Hareket isimlerini kaydet
    with open('hareket_isimleri.pkl', 'wb') as f:
        pickle.dump(hareketler, f)
    print("✅ Hareket isimleri 'hareket_isimleri.pkl' olarak kaydedildi!")
    
    # Test sonuçları
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"\n🎯 Test Doğruluğu: {accuracy*100:.2f}%")
    print(f"📉 Test Kaybı: {loss:.4f}")
    print("=" * 60)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("EL HAREKETİ TANIMA MODELİ EĞİTİMİ")
    print("=" * 60)
    print("\nHazır datasetten model eğitilecek.")
    print("Varsayılan klasör: 'veri/'")
    print("\nFarklı bir klasör kullanmak ister misiniz?")
    print("(Varsayılan için Enter, değiştirmek için klasör yolunu yazın)")
    
    dataset_klasoru = input("Dataset klasörü: ").strip()
    if not dataset_klasoru:
        dataset_klasoru = 'veri'
    
    print(f"\n📂 Kullanılacak klasör: {dataset_klasoru}")
    print("\nDevam edilsin mi? (Enter'a basın)")
    input()
    
    model_egit(dataset_klasoru)
