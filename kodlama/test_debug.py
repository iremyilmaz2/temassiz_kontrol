print("1: Modüller yükleniyor...")
try:
    import cv2
    print("2: OpenCV yüklendi.")
    import mediapipe as mp
    print("3: MediaPipe yüklendi.")
    from keras.models import load_model
    print("4: Keras yüklendi.")
    from flask_socketio import SocketIO
    print("5: SocketIO yüklendi.")
except Exception as e:
    print(f"HATA OLUŞTU: {e}")

print("Test bitti.")