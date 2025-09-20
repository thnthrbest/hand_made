import cv2
import numpy as np
from ultralytics import YOLO
import socket
import struct
import threading

# --- Configuration ---
NowRun = True
ShowDebugScreen = True  

# Background remove color
BG_COLOR = (0, 0, 0)

# Setup Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockImg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverAddressPortSendResults = ("127.0.0.1", 6063)

# โหลด YOLO ที่เทรน detect มือ
model_path = "C:/hand-shadow-ai/model/bestV4.pt"
try:
    model_shadow = YOLO(model_path)
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

# Wait For Connection From Unity
sockImg.bind(("127.0.0.1", 6066))
sockImg.listen(1)
print("Waiting for connection...")
client_socket, client_address = sockImg.accept()
print(f"Connected to {client_address}")

while True:
    # Receive the length of the incoming frame
    length_data = client_socket.recv(4)
    if not length_data:
        break
    length = struct.unpack('I', length_data)[0]

    # Receive the image data from Unity
    image_data = b""
    while len(image_data) < length:
        image_data += client_socket.recv(length - len(image_data))

    # Decode image
    np_arr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) 
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    output = np.zeros_like(frame)

    # -------------------------
    # YOLO ตรวจจับ "มือ"
    # -------------------------
    results = model_shadow(frame, conf=0.5)
    for r in results:
        for box in r.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box[:4])
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            hand_roi = frame[y1:y2, x1:x2]

            # -------------------------
            # 1. ตัด BG → ใช้กล่อง YOLO
            # -------------------------
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            mask[y1:y2, x1:x2] = 255
            hand_only = cv2.bitwise_and(frame, frame, mask=mask)

            # -------------------------
            # 2. แปลงเป็นขาวดำ
            # -------------------------
            gray = cv2.cvtColor(hand_roi, cv2.COLOR_BGR2GRAY)
            hand_gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

            # -------------------------
            # 3. ใส่ลง output
            # -------------------------
            output[y1:y2, x1:x2] = hand_gray

    # -------------------------
    # ส่งผลกลับ Unity
    # -------------------------
    _, img_encoded = cv2.imencode('.jpg', output)
    processed_data = img_encoded.tobytes()
    client_socket.send(struct.pack('I', len(processed_data)))
    client_socket.send(processed_data)

    if ShowDebugScreen:
        cv2.imshow("Original", frame)
        cv2.imshow("YOLO Hand Gray", output)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

NowRun = False
client_socket.close()
sockImg.close()
cv2.destroyAllWindows()
