import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO
import socket
import struct
import threading
import time
import random

# Initialize MediaPipe For Hand
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

# Initialize MediaPipe Selfie Segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=0) # 0 for general model, 1 for landscape
mp_drawing_bg = mp.solutions.drawing_utils


# --- Configuration ---

# Normal function
detect = False # use for check it use detection, or not so has detect = True, detect = False 
NowRun = True # use for recive value form unity, this recive = True, stop = False, this feature has useful
ShowDebugScreen = False # show screen for debug value, default is close = False, open = True
checkc = False
# Detection value
thres = 70 # it adjust for hand skin color this value has a few is white, and this much it has dim, default is 70
handScale = 50 # size of Detect box default value is 50

# Bg Remove
# Choose your background type: "color" now only has color
BACKGROUND_TYPE = "color" 

# For "color" background
BG_COLOR = (0, 0, 0)  # Adjust for Background Color, this use BGR format, Default is black (0,0,0)



# Setup Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockImg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverAddressPort = ("127.0.0.1", 5052) # Send hand position
serverAddressPortSendResults = ("127.0.0.1", 5053) # Send Pose Detection Result


# Load Pose Detection model use YOLO V11

# model_path = f"D:/GitHub/hand_made/python_handmade/model/best.pt"


# try:
#     model_shadow = YOLO(model_path)
# except Exception as e:
#     print(f"Error loading model or labels: {e}")
#     exit(1)
    
    
animal = ["rabbit","elephent","snail","dog","deer","cow","crab","bird"]
random_animal = ""


# Recive Value form unity
def ReciveValue():
    global detect, thres , checkc
    sock_unity_revice = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_unity_revice.bind(("127.0.0.1", 5051))
    print(f"Listening on Unity")

    while True:
        if not NowRun:
            break
        data, addr = sock_unity_revice.recvfrom(1024)  # buffer size is 1024 bytes
        data = data.decode('utf-8')
        
        print("Received message:", data)
        if data == "True":
            checkc = True
            detect = True
        elif data == "False":
            detect = False
        else:
            try:
                thres  = int(data)
                print(thres)
            except Exception as e:
                print(e)
                
    
# Filter for Silhouette
def apply_filters(roi, brightness, contrast, saturation, warmth):
    roi = cv2.convertScaleAbs(roi, alpha=contrast / 50.0, beta=brightness - 50)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hsv[..., 1] = np.clip(hsv[..., 1] * (saturation / 50.0), 0, 255)
    roi = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    b, g, r = cv2.split(roi)
    r = np.clip(r + (warmth - 50), 0, 255).astype(np.uint8)
    roi = cv2.merge((b, g, r))
   
    return roi

#  Wait For Connection From Unity
sockImg.bind(("127.0.0.1", 5055))
sockImg.listen(1)
print("Waiting for connection...")
client_socket, client_address = sockImg.accept()
print(f"Connected to {client_address}")
unity_recive_state_thread = threading.Thread(target=ReciveValue)
unity_recive_state_thread.start()

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
    
    # Convert the image data to a NumPy array and decode it
    np_arr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) 
    frame = img

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    original = frame.copy()

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultsBg = selfie_segmentation.process(rgb_frame)
    condition = np.stack((resultsBg.segmentation_mask,) * 3, axis=-1) > 0.1 # Threshold can be adjusted


    
    # Remove BackGround for Balck Color 
    # Color can adjust in BG_COLOR
    if BACKGROUND_TYPE == "color":
            background = np.zeros(frame.shape, dtype=np.uint8)
            background[:] = BG_COLOR

    output_frame = np.where(condition, frame, background)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    output = np.zeros_like(output_frame)

    #Find a hand landmarks 
    if results.multi_hand_landmarks:
        PosXmin = []
        PosXmax = []
        PosYmin = []
        PosYmax = []
        SendHandData = [] 
        SendValue = ""
        for hand_landmarks in results.multi_hand_landmarks:
            SendHandData = []
            x_coords = [lm.x * w for lm in hand_landmarks.landmark]
            y_coords = [lm.y * h for lm in hand_landmarks.landmark]
            z_coords = [lm.z * h for lm in hand_landmarks.landmark]
            x_min, x_max = int(min(x_coords)) - handScale, int(max(x_coords)) + handScale
            y_min, y_max = int(min(y_coords)) - handScale, int(max(y_coords)) + handScale
            x_min, x_max = max(x_min, 0), min(x_max, w)
            y_min, y_max = max(y_min, 0), min(y_max, h)
          
            try:
                for X, Y, Z in zip(x_coords, y_coords, z_coords):
                    SendHandData.extend([int(X), int(h-Y), int(Z)])
                SendValue += f'{str(SendHandData)}_' 
            except Exception as e:
                print("add value error", e)

            # Crop only hand position for accuracy
            try:
               PosXmin.append(x_min)
               PosXmax.append(x_max)
               PosYmin.append(y_min)
               PosYmax.append(y_max)
   
            except Exception as e:
                print(f"Shadow detection error: {e}")
                
 
            hand_roi = output_frame[y_min:y_max, x_min:x_max]
            # if scale != 1.0:
            #     hand_roi = cv2.resize(hand_roi, None, fx=scale, fy=scale)
            gray = cv2.cvtColor(hand_roi, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, thres, 255, cv2.THRESH_BINARY_INV)

            hand_canvas = np.zeros_like(hand_roi)
            hand_canvas[:] = (255,255,255)
            mask_3ch = cv2.merge([mask, mask, mask])
            hand_result = np.where(mask_3ch == 255, hand_canvas, 0)

            # Apply filters to hand only
            hand_filtered = apply_filters(hand_result, 50, 50, 50, 50)

            # Resize back to original
            hand_filtered = cv2.resize(hand_filtered, (x_max - x_min, y_max - y_min))
            output[y_min:y_max, x_min:x_max] = hand_filtered

            mp_drawing.draw_landmarks(original, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        # Send hand landmark to Unity
        #   sock.sendto(str.encode(SendValue[:len(SendValue)-1]), serverAddressPort)

    
    # Pose Detection
    if detect:
        print(NowRun)
        try:
            
            if checkc:
                random_animal = random.choice(animal)
                model_path = f"D:/GitHub/hand_made/python_handmade/model/{random_animal}.pt"
                # Load models and labels
                try:
                    model_shadow = YOLO(model_path)
                except Exception as e:
                    #print(f"Error loading models or labels: {e}")
                    exit(1)
                checkc = False
            

            results_shadow = model_shadow(output, show=False) # YOLO Detection models 
            for shadow_result in results_shadow:
                shadow_boxes = shadow_result.boxes
                if shadow_boxes is not None:
                    for shadow_box in shadow_boxes:
                        # Bounding box coordinates
                        x1s, y1s, x2s, y2s = map(int, shadow_box.xyxy[0].tolist())
                        
                        # Confidence and class
                        conf_s = float(shadow_box.conf[0])
                        cls_s = int(shadow_box.cls[0])
                        
                        # Draw rectangle
                        #cv2.rectangle(output, (x1s, y1s), (x2s, y2s), (0, 255, 0), 2)
                        
                        # Label
                        label_text = f"{model_shadow.names[cls_s]} {conf_s:.2f}"
                        sock.sendto(str.encode(label_text), serverAddressPort)
                        
                        #cv2.putText(output, label_text, (x1s, y1s - 10), 
                                #cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        except Exception as e:
            print(f"Shadow detection error: {e}")
                 
   
    # Send Process Image To Unity 
    _, img_encoded = cv2.imencode('.jpg', output)
    processed_data = img_encoded.tobytes()
    
    # Send the length of the processed frame and the frame itself
    client_socket.send(struct.pack('I', len(processed_data)))
    client_socket.send(processed_data)
    if ShowDebugScreen:
        cv2.imshow("Original", original)
        cv2.imshow("Filtered Hand", output)
        cv2.imshow('Webcam Background Removal - Press Q to Quit', output_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('d'):  #เปลี่ยนการตรวจจับ
            detect = not detect
            print(f"Detec mode: {'ON' if detect else 'OFF'}")
        elif key == ord('q'):  # Quit
            break
        
# Clean up
NowRun = False
print("clean")
client_socket.close()
sockImg.close()
cv2.destroyAllWindows()
