import { useEffect, useState, useRef } from "react";
import io from "socket.io-client";
import Webcam from "react-webcam";

function App() {
  const [isExternal, setIsExternal] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [komut, setKomut] = useState("Sistem Hazır");
  const [isCapturing, setIsCapturing] = useState(false);
  const [isLocked, setIsLocked] = useState(false);
  const [socket, setSocket] = useState(null);
  const webcamRef = useRef(null);

  const MY_IP = "172.16.40.63"; // Kendi IPv4 adresinle güncellemeyi unutma!

  // 1. Senin belirlediğin yeni el hareketleri ve açıklamaları
  const hareketTanimlari = {
    "duraklat": "Durdur",
    "oynat": "Oynat",
    "video_ileri": "10 sn ileri sar",
    "video_geri": "10 sn geri sar",
    "sonraki_video": "Sonraki Video",
    "onceki_video": "Önceki Video",
    "tam_ekran": "Tam Ekran",
    "kucuk_ekran": "Küçük Ekran",
    "ekran_goruntusu": "Ekran Görüntüsü Al"
  };

  // 2. Seçilebilir aksiyonlar (Tam liste)
  const tumAksiyonlar = [
    { id: "duraklat", label: "Tüm Parmaklar Açık🖐️" },
    { id: "oynat", label: "Yumruk Yap ✊"},
    { id: "tam_ekran", label: "İşaret ve Başparmak Açık (L)👆" },
    { id: "kucuk_ekran", label: "İşaret ve Başparmak Kapalı👌" },
    { id: "video_ileri", label: "İki Parmak Sağa ✌️➡️" },
    { id: "video_geri", label: "İki Parmak Sola ⬅️✌️" },
    { id: "sonraki_video", label: "Üç Parmak Sağa ➡️" },
    { id: "onceki_video", label: "Üç Parmak Sola ⬅️" },
    { id: "ekran_goruntusu", label: "Başparmak Yukarı 👍" }
  ];

  const [mapping, setMapping] = useState(() => {
    const saved = localStorage.getItem("handMapping");
    if (saved) return JSON.parse(saved);
    // Varsayılan eşleşme: Her hareketi kendi mantıklı karşılığına ata
    const initial = {};
    Object.keys(hareketTanimlari).forEach(h => initial[h] = h);
    return initial;
  });

  useEffect(() => {
    const targetIP = isExternal ? `http://${MY_IP}:5000` : "http://localhost:5000";
    const newSocket = io(targetIP);
    setSocket(newSocket);

    newSocket.on("gesture_command", (data) => {
      setKomut(data.command);
      setIsLocked(true);
      setTimeout(() => setIsLocked(false), 2000);
    });

    return () => newSocket.disconnect();
  }, [isExternal]);

  useEffect(() => {
    let interval;
    if (isCapturing && socket) {
      interval = setInterval(() => {
        if (webcamRef.current && !isLocked) {
          const imageSrc = webcamRef.current.getScreenshot();
          if (imageSrc) {
            socket.emit("process_frame", { 
              image: imageSrc.split(",")[1],
              user_mapping: mapping 
            });
          }
        }
      }, 200);
    }
    return () => clearInterval(interval);
  }, [isCapturing, isLocked, socket, mapping]);

  const handleUpdateMapping = (hareket, yeniAksiyon) => {
    const newMapping = { ...mapping, [hareket]: yeniAksiyon };
    setMapping(newMapping);
    localStorage.setItem("handMapping", JSON.stringify(newMapping));
  };

  return (
    <div style={{ textAlign: "center", backgroundColor: "#121212", minHeight: "100vh", color: "white", padding: "20px", fontFamily: 'Segoe UI' }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", maxWidth: "950px", margin: "0 auto 20px auto" }}>
        <h2 style={{ color: "#00d4ff", margin: 0 }}>TÜBİTAK Temassız Kontrol Paneli</h2>
        <button onClick={() => setShowSettings(!showSettings)} style={{ padding: "10px 25px", cursor: "pointer", borderRadius: "8px", background: "#333", color: "white", border: "1px solid #555", fontWeight: 'bold' }}>
          {showSettings ? "✖ Kapat" : "⚙️ Kişiselleştir"}
        </button>
      </div>

      {showSettings && (
        <div style={{ background: "#1e1e1e", padding: "25px", borderRadius: "15px", marginBottom: "25px", textAlign: "left", maxWidth: "600px", margin: "0 auto 25px auto", border: "1px solid #333", boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
          <h3 style={{ color: "#00d4ff", marginTop: 0, borderBottom: '1px solid #333', paddingBottom: '10px' }}>Hareket ve Komut Eşleştirmesi</h3>
          <div style={{ maxHeight: '400px', overflowY: 'auto', paddingRight: '10px' }}>
            {Object.keys(mapping).map((hareketAnahtari) => (
              <div key={hareketAnahtari} style={{ display: "flex", justifyContent: "space-between", marginBottom: "15px", alignItems: "center" }}>
                <span style={{ fontWeight: "600", fontSize: '15px', color: '#ccc' }}>{hareketTanimlari[hareketAnahtari]}:</span>
                <select 
                  value={mapping[hareketAnahtari]} 
                  onChange={(e) => handleUpdateMapping(hareketAnahtari, e.target.value)}
                  style={{ padding: "8px", borderRadius: "6px", background: "#2a2a2a", color: "white", border: "1px solid #444", width: "200px", cursor: 'pointer' }}
                >
                  {tumAksiyonlar.map(a => <option key={a.id} value={a.id}>{a.label}</option>)}
                </select>
              </div>
            ))}
          </div>
          <button onClick={() => { localStorage.removeItem("handMapping"); window.location.reload(); }} style={{ width: "100%", padding: "12px", marginTop: "15px", backgroundColor: "#ff4b2b", color: "white", border: "none", borderRadius: "8px", cursor: "pointer", fontWeight: 'bold' }}>Ayarları Sıfırla</button>
        </div>
      )}

      <div style={{ marginBottom: "30px" }}>
        <button onClick={() => setIsExternal(false)} style={{ padding: "12px 25px", cursor: "pointer", border: "none", background: !isExternal ? "#00d4ff" : "#333", color: "white", borderRadius: "10px 0 0 10px", fontWeight: 'bold' }}>Yerel Bilgisayar</button>
        <button onClick={() => setIsExternal(true)} style={{ padding: "12px 25px", cursor: "pointer", border: "none", background: isExternal ? "#00d4ff" : "#333", color: "white", borderRadius: "0 10px 10px 0", fontWeight: 'bold' }}>Dış Bilgisayar (Ağ)</button>
      </div>

      <button onClick={() => setIsCapturing(!isCapturing)} style={{ padding: "18px 60px", marginBottom: "40px", fontSize: "20px", fontWeight: "bold", backgroundColor: isCapturing ? "#ff4b2b" : "#00c853", color: "white", border: "none", borderRadius: "15px", cursor: "pointer", transition: '0.3s', boxShadow: '0 5px 25px rgba(0,0,0,0.4)' }}>
        {isCapturing ? "🔴 SİSTEMİ DURDUR" : "🟢 SİSTEMİ BAŞLAT"}
      </button>

      <div style={{ display: "flex", justifyContent: "center", gap: "40px", flexWrap: "wrap" }}>
        <div style={{ border: `6px solid ${isLocked ? '#ff4b2b' : '#00d4ff'}`, borderRadius: "25px", overflow: "hidden", position: "relative" }}>
          <Webcam ref={webcamRef} mirrored={true} width={480} height={360} screenshotFormat="image/jpeg" />
          {isLocked && <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "24px", fontWeight: "bold", color: '#00d4ff' }}>KOMUT GÖNDERİLDİ</div>}
        </div>
        <div style={{ background: "#1e1e1e", padding: "40px", borderRadius: "25px", minWidth: "320px", border: "1px solid #333", display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h3 style={{ color: "#aaa", margin: 0, fontSize: '14px', letterSpacing: '2px' }}>DURUM</h3>
          <h1 style={{ fontSize: "52px", color: isLocked ? "#ff4b2b" : "#00d4ff", margin: "20px 0" }}>{komut.replace("_", " ").toUpperCase()}</h1>
          <p style={{ color: "#555" }}>{isLocked ? "2sn bekleyin..." : "Bir hareket yapın"}</p>
        </div>
      </div>
    </div>
  );
}

export default App;