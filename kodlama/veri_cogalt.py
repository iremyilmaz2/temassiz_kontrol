import cv2
import numpy as np
import os
from glob import glob

# Hareketler
hareketler = ["duraklat", "oynat", "ses_ac", "ses_kapat", "onceki_video", 
              "sonraki_video", "video_ileri", "video_geri", "tam_ekran", 
              "kucuk_ekran", "ekran_goruntusu"]

def bulaniklastir(img):
    """Görüntüyü bulanıklaştır"""
    kernel_size = np.random.choice([3, 5, 7])
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

def gurultu_ekle(img):
    """Gaussian gürültü ekle"""
    mean = 0
    sigma = np.random.uniform(10, 30)
    gauss = np.random.normal(mean, sigma, img.shape).astype('uint8')
    noisy = cv2.add(img, gauss)
    return noisy

def grilestirilmis(img):
    """Görüntüyü gri tonlamalı yap ve tekrar RGB'ye çevir"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def parlaklik_degistir(img):
    """Parlaklığı değiştir"""
    beta = np.random.randint(-50, 50)
    return cv2.convertScaleAbs(img, alpha=1.0, beta=beta)

def kontrast_degistir(img):
    """Kontrastı değiştir"""
    alpha = np.random.uniform(0.7, 1.3)
    return cv2.convertScaleAbs(img, alpha=alpha, beta=0)

def yakinlastir(img):
    """Görüntüyü rastgele yakınlaştır/uzaklaştır"""
    scale = np.random.uniform(0.9, 1.1)
    h, w = img.shape[:2]
    new_h, new_w = int(h * scale), int(w * scale)
    resized = cv2.resize(img, (new_w, new_h))
    
    if scale > 1:
        # Kırp
        start_h = (new_h - h) // 2
        start_w = (new_w - w) // 2
        return resized[start_h:start_h+h, start_w:start_w+w]
    else:
        # Padding ekle
        pad_h = (h - new_h) // 2
        pad_w = (w - new_w) // 2
        return cv2.copyMakeBorder(resized, pad_h, pad_h, pad_w, pad_w, 
                                  cv2.BORDER_REPLICATE)

def yatay_cevir(img):
    """Görüntüyü yatay çevir (ayna efekti)"""
    return cv2.flip(img, 1)

def renk_kaydir(img):
    """Renkleri hafifçe kaydır"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    h = (h + np.random.randint(-10, 10)) % 180
    hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def veri_cogalt():
    # Giriş ve çıkış klasörlerini belirle
    giris_klasor = 'orjinal_foto'  # Buraya fotoğraflarınızı koyun
    cikis_klasor = 'veri'
    
    if not os.path.exists(cikis_klasor):
        os.makedirs(cikis_klasor)
    
    # Augmentation teknikleri
    augmentasyonlar = [
        ("bulanik", bulaniklastir),
        ("gurultu", gurultu_ekle),
        ("gri", grilestirilmis),
        ("parlak", parlaklik_degistir),
        ("kontrast", kontrast_degistir),
        ("zoom", yakinlastir),
        ("renk", renk_kaydir),
        ("orijinal", lambda x: x),  # Orijinal görüntü
    ]
    
    for hareket in hareketler:
        print(f"\n{hareket.upper()} için veri çoğaltılıyor...")
        
        # Çıkış klasörünü oluştur
        hareket_cikis = os.path.join(cikis_klasor, hareket)
        os.makedirs(hareket_cikis, exist_ok=True)
        
        # Hareket klasörünü oluştur
        hareket_klasor = os.path.join(giris_klasor, hareket)
        
        if not os.path.exists(hareket_klasor):
            print(f"UYARI: {hareket_klasor} klasörü bulunamadı! Atlanıyor...")
            continue
        
        # Tüm fotoğrafları al
        foto_yollari = glob(os.path.join(hareket_klasor, "*.jpg")) + \
                       glob(os.path.join(hareket_klasor, "*.png")) + \
                       glob(os.path.join(hareket_klasor, "*.jpeg"))
        
        if len(foto_yollari) == 0:
            print(f"UYARI: {hareket} klasöründe fotoğraf bulunamadı!")
            continue
        
        print(f"Bulunan orijinal fotoğraf sayısı: {len(foto_yollari)}")
        
        kayit_sayaci = 0
        
        # Her fotoğraf için
        for foto_idx, foto_yol in enumerate(foto_yollari):
            img = cv2.imread(foto_yol)
            
            if img is None:
                print(f"UYARI: {foto_yol} okunamadı!")
                continue
            
            # Her augmentasyon tekniğini uygula ve kaydet
            for aug_isim, aug_fonksiyon in augmentasyonlar:
                try:
                    # Augmentasyon uygula
                    aug_img = aug_fonksiyon(img.copy())
                    
                    # Fotoğrafı kaydet
                    cikis_yol = os.path.join(hareket_cikis, 
                                            f'{hareket}_{foto_idx}_{aug_isim}.jpg')
                    cv2.imwrite(cikis_yol, aug_img)
                    kayit_sayaci += 1
                    
                except Exception as e:
                    print(f"Hata ({aug_isim}): {e}")
                    continue
            
            # Ek varyasyonlar: Birden fazla augmentasyon birleştir
            for kombi_idx in range(5):  # Her fotoğraf için 5 rastgele kombinasyon
                try:
                    aug_img = img.copy()
                    
                    # Rastgele 2-3 augmentasyon seç ve uygula
                    secilen_aug = np.random.choice(len(augmentasyonlar), 
                                                   size=np.random.randint(2, 4), 
                                                   replace=False)
                    
                    for idx in secilen_aug:
                        aug_isim, aug_fonksiyon = augmentasyonlar[idx]
                        aug_img = aug_fonksiyon(aug_img)
                    
                    # Fotoğrafı kaydet
                    cikis_yol = os.path.join(hareket_cikis, 
                                            f'{hareket}_{foto_idx}_kombi{kombi_idx}.jpg')
                    cv2.imwrite(cikis_yol, aug_img)
                    kayit_sayaci += 1
                        
                except Exception as e:
                    continue
        
        # Sonuçları yazdır
        if kayit_sayaci > 0:
            print(f"✓ {hareket}: {kayit_sayaci} fotoğraf kaydedildi")
            print(f"  Çoğaltma oranı: {len(foto_yollari)} → {kayit_sayaci}")
        else:
            print(f"✗ {hareket}: Hiç fotoğraf kaydedilemedi!")
    
    print("\n✓ Tüm fotoğraflar çoğaltıldı ve kaydedildi!")
    print(f"\nKaydedilen klasör: {os.path.abspath(cikis_klasor)}")

if __name__ == "__main__":
    print("Veri Çoğaltma Aracı (Fotoğraf Üretimi)")
    print("=" * 50)
    print("\nKlasör yapısı şu şekilde olmalı:")
    print("orjinal_foto/")
    print("  ├── duraklat/")
    print("  │   ├── foto1.jpg")
    print("  │   ├── foto2.jpg")
    print("  │   └── ...")
    print("  ├── oynat/")
    print("  │   └── ...")
    print("  └── ...")
    print("\nÇıktı klasörü:")
    print("veri/")
    print("  ├── duraklat/")
    print("  │   ├── duraklat_0_bulanik.jpg")
    print("  │   ├── duraklat_0_gurultu.jpg")
    print("  │   └── ...")
    print("  └── ...")
    print("\nDevam edilsin mi? (Evet için Enter'a basın)")
    input()
    
    veri_cogalt()