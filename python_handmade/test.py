import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO
import random
# Initialize MediaPipe For Hand
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

# Initialize MediaPipe Selfie Segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=0) # 0 for general model, 1 for landscape
mp_drawing_bg = mp.solutions.drawing_utils


save_crop = False  # Set to True only when you want to save
frame_id = 0  # Increment this after each save
model_animal ="best.pt"
# YOLO PoseDetection Model Path
model_path = f"D:/GitHub/hand_made/python_handmade/model/{model_animal}"

# Load models and labels
try:
    model_shadow = YOLO(model_path)
except Exception as e:
    print(f"Error loading models or labels: {e}")
    exit(1)
# --- Configurati

# Bg Remove
BACKGROUND_TYPE = "color"  # Change this to "color", "image", or "blur"

# For "color" background
BG_COLOR = (0, 0, 0)  # background color in BGR format

play = False
animal = ["cat", "dog", "elephent", "bird", "fish"]
random_animal = "x"

# Webcam
cap = cv2.VideoCapture(1)

cv2.namedWindow("Controls", cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow("Controls", 500, 100)
def nothing(x): pass

# Create adjustment sliders
cv2.createTrackbar("Threshold", "Controls", 70, 255, nothing)
cv2.createTrackbar("handScale", "Controls", 20, 255, nothing)

def apply_filters(roi, brightness, contrast, saturation, warmth):
    roi = cv2.convertScaleAbs(roi, alpha=contrast / 50.0, beta=brightness - 50)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hsv[..., 1] = np.clip(hsv[..., 1] * (saturation / 50.0), 0, 255)
    roi = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    b, g, r = cv2.split(roi)
    r = np.clip(r + (warmth - 50), 0, 255).astype(np.uint8)
    roi = cv2.merge((b, g, r))
    
    return roi

while True:
 
    try:
        ret, frame = cap.read()
        if not ret:
            cap.release()
            

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        original = frame.copy()

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultsBg = selfie_segmentation.process(rgb_frame)
        condition = np.stack((resultsBg.segmentation_mask,) * 3, axis=-1) > 0.1 # Threshold can be adjusted
        
        if BACKGROUND_TYPE == "color":
                background = np.zeros(frame.shape, dtype=np.uint8)
                background[:] = BG_COLOR

        output_frame = np.where(condition, frame, background)
        
        # Get slider values
        thresh = cv2.getTrackbarPos("Threshold", "Controls")
        handScale = cv2.getTrackbarPos("handScale", "Controls")
        
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        output = np.zeros_like(output_frame)
        
        if results.multi_hand_landmarks:
            PosXmin = []
            PosXmax = []
            PosYmin = []
            PosYmax = []
        
            SendValue = ""
            for hand_landmarks in results.multi_hand_landmarks:
                
                x_coords = [lm.x * w for lm in hand_landmarks.landmark]
                y_coords = [lm.y * h for lm in hand_landmarks.landmark]
                z_coords = [lm.z * h for lm in hand_landmarks.landmark]
                x_min, x_max = int(min(x_coords)) - handScale, int(max(x_coords)) + handScale
                y_min, y_max = int(min(y_coords)) - handScale, int(max(y_coords)) + handScale
                x_min, x_max = max(x_min, 0), min(x_max, w)
                y_min, y_max = max(y_min, 0), min(y_max, h)

                try:
                    PosXmin.append(x_min)
                    PosXmax.append(x_max)
                    PosYmin.append(y_min)
                    PosYmax.append(y_max)
    
                except Exception as e:
                    print(f"Shadow detection error: {e}")
                    
    
                hand_roi = output_frame[y_min:y_max, x_min:x_max]
                
                gray = cv2.cvtColor(hand_roi, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY_INV)

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
        
    except Exception as e:
        print(f"Shadow detection error: {e}")
        
    if play:
        try:
            results_shadow = model_shadow(output, show=False)
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
                        cv2.rectangle(output, (x1s, y1s), (x2s, y2s), (0, 255, 255), 2)
                        
                        # Label
                        label_text = f"{model_shadow.names[cls_s]} {conf_s:.2f}"
                
                        print(label_text)
                        cv2.putText(original, label_text, (25, 75), 
                                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        
        except Exception as e:
            print(f"Shadow detection error: {e}")
    
    cv2.putText(original, f'Animal : {random_animal}', (25, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


    cv2.imshow("Original", original)
    cv2.imshow('Webcam Background Removal', output_frame)
    cv2.imshow("Filtered Hand", output)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Quit
        break
    elif key == ord('a'):
        play = not play
        random_animal = random.choice(animal)


cap.release()
cv2.destroyAllWindows()