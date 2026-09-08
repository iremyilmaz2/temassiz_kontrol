# Temassız Medya ve Cihaz Kontrolü (Contactless Media Control)

Bu proje; bilgisayarla görme (Computer Vision) ve derin öğrenme modelleri kullanarak el hareketleriyle (gestures) temassız medya oynatma, cihaz eşleştirme ve uzaktan kontrol imkânı sunan uçtan uca bir sistemdir.

## 🚀 Özellikler

- **Gerçek Zamanlı El Takibi & Hareket Algılama:** OpenCV ve derin öğrenme modelleri ile düşük gecikmeli hareket tanıma.
- **WebSocket Tabanlı Çift Yönlü İletişim:** Algılanan hareket komutlarının istemcilere anlık iletilmesi.
- **Cihaz Eşleştirme & Çoklu Kullanıcı Güvenliği:** Eşleşme kodu ile oturum bazlı güvenli cihaz bağlantısı.
- **Modern Web Arayüzü:** React ile geliştirilmiş responsive kontrol ve izleme paneli.
- **Konteynerizasyon:** Docker ve Docker Compose ile hızlı ve taşınabilir kurulum.

---

## 🛠️ Kullanılan Teknolojiler

- **Backend & Bilgisayarla Görme:** Python, OpenCV, TensorFlow / Keras, WebSockets
- **Frontend:** React, Vite, JavaScript, CSS
- **DevOps & Dağıtım:** Docker, Docker Compose, Nginx

---

## 💻 Kurulum ve Çalıştırma

### 1. Depoyu Klonlayın
```bash
git clone [https://github.com/iremyilmaz2/temassiz_kontrol.git](https://github.com/iremyilmaz2/temassiz_kontrol.git)
cd temassiz_kontrol

```

### 2. Docker ile Çalıştırma (Önerilen)

```bash
docker compose up --build

```

### 3. Manuel Kurulum

**Backend:**

```bash
cd kodlama
pip install -r requirements.txt
python web_server.py

```

**Frontend:**

```bash
cd TemassizKontrolProjesi
npm install
npm run dev

```

---

## 📄 Lisans

Bu proje eğitim ve kişisel portföy amacıyla açık kaynak olarak sunulmuştur.

```
