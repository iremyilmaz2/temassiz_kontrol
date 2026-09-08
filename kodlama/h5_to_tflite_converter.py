import tensorflow as tf
import numpy as np

def convert_h5_to_tflite(h5_model_path, tflite_model_path, quantize=False):
    # Keras modelini yükle
    print(f"Model yükleniyor: {h5_model_path}")
    model = tf.keras.models.load_model(h5_model_path)
    
    # Model özetini göster
    print("\nModel Özeti:")
    model.summary()
    
    # TFLite converter oluştur
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Quantization (isteğe bağlı - model boyutunu küçültür)
    if quantize:
        print("\nQuantization uygulanıyor...")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        # Float16 quantization için:
        # converter.target_spec.supported_types = [tf.float16]
    
    # Modeli dönüştür
    print("\nModel TFLite formatına dönüştürülüyor...")
    tflite_model = converter.convert()
    
    # TFLite modelini kaydet
    with open(tflite_model_path, 'wb') as f:
        f.write(tflite_model)
    
    print(f"\n✓ Model başarıyla dönüştürüldü: {tflite_model_path}")
    
    # Dosya boyutlarını karşılaştır
    import os
    original_size = os.path.getsize(h5_model_path) / (1024 * 1024)  # MB
    tflite_size = os.path.getsize(tflite_model_path) / (1024 * 1024)  # MB
    
    print(f"\nDosya Boyutları:")
    print(f"  Orijinal (.h5): {original_size:.2f} MB")
    print(f"  TFLite (.tflite): {tflite_size:.2f} MB")
    print(f"  Boyut azalması: {((original_size - tflite_size) / original_size * 100):.1f}%")
    
    return tflite_model


def test_tflite_model(tflite_model_path, input_shape):
    """
    TFLite modelini test eder (isteğe bağlı)
    
    Args:
        tflite_model_path: TFLite model dosyasının yolu
        input_shape: Giriş tensörünün şekli, örn: (1, 224, 224, 3)
    """
    print(f"\nTFLite modeli test ediliyor...")
    
    # TFLite interpreter oluştur
    interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
    interpreter.allocate_tensors()
    
    # Giriş ve çıkış detaylarını al
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    print("\nGiriş Detayları:")
    print(f"  Şekil: {input_details[0]['shape']}")
    print(f"  Tip: {input_details[0]['dtype']}")
    
    print("\nÇıkış Detayları:")
    print(f"  Şekil: {output_details[0]['shape']}")
    print(f"  Tip: {output_details[0]['dtype']}")
    
    # Test verisi oluştur
    test_input = np.random.random(input_shape).astype(np.float32)
    
    # Tahmin yap
    interpreter.set_tensor(input_details[0]['index'], test_input)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])
    
    print(f"\n✓ Model başarıyla çalışıyor!")
    print(f"  Çıkış şekli: {output.shape}")


if __name__ == "__main__":
    # Kullanım örneği
    
    # Model dosya yollarını belirtin
    H5_MODEL_PATH = "el_hareket_modeli.h5"  # Sizin .h5 model dosyanızın yolu
    TFLITE_MODEL_PATH = "model.tflite"  # Çıkış dosyası adı
    
    # Dönüştürme işlemini çalıştır
    try:
        # Quantization OLMADAN dönüştür (daha yüksek doğruluk)
        convert_h5_to_tflite(H5_MODEL_PATH, TFLITE_MODEL_PATH, quantize=False)
        
        # Quantization İLE dönüştür (daha küçük dosya boyutu)
        # convert_h5_to_tflite(H5_MODEL_PATH, TFLITE_MODEL_PATH, quantize=True)
        
        # Test etmek isterseniz (input_shape'i modelinize göre ayarlayın):
        # test_tflite_model(TFLITE_MODEL_PATH, input_shape=(1, 224, 224, 3))
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {str(e)}")
        print("\nLütfen model dosya yolunun doğru olduğundan emin olun.")