import cv2
import mediapipe as mp
import math
import pyautogui
import numpy as np

# --- 1. AJUSTES DE RENDIMIENTO ---
# Aumentamos alpha para un control más responsivo (menos lag)
alpha = 0.6 
PINCH_THRESHOLD = 20
FRAME_PADDING = 100

# Eliminamos la pausa de PyAutoGUI para máxima velocidad
pyautogui.PAUSE = 0

# --- ESTADO DEL CONTROLADOR ---
click_lock = False

# --- INICIALIZACIÓN DE LIBRERÍAS ---
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0)

# --- 2. REDUCIR LA RESOLUCIÓN DE LA CÁMARA ---
# Establecemos una resolución más baja. 640x480 es un estándar muy rápido.
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Obtener las dimensiones de la pantalla del monitor
screen_w, screen_h = pyautogui.size()

# Variables de suavizado
smoothed_ix, smoothed_iy = None, None
smoothed_tx, smoothed_ty = None, None

with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5) as hands:
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Esta es la operación más costosa
        results = hands.process(image_rgb)
        
        cv2.rectangle(frame, (FRAME_PADDING, FRAME_PADDING), (w - FRAME_PADDING, h - FRAME_PADDING), (255, 255, 0), 2)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # (El resto de la lógica de detección y suavizado es la misma)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            raw_ix, raw_iy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            if smoothed_ix is None: smoothed_ix, smoothed_iy = raw_ix, raw_iy
            else:
                smoothed_ix = int(alpha * raw_ix + (1 - alpha) * smoothed_ix)
                smoothed_iy = int(alpha * raw_iy + (1 - alpha) * smoothed_iy)

            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            raw_tx, raw_ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
            if smoothed_tx is None: smoothed_tx, smoothed_ty = raw_tx, raw_ty
            else:
                smoothed_tx = int(alpha * raw_tx + (1 - alpha) * smoothed_tx)
                smoothed_ty = int(alpha * raw_ty + (1 - alpha) * smoothed_ty)

            distance = math.dist((smoothed_ix, smoothed_iy), (smoothed_tx, smoothed_ty))
            pinch_active = distance < PINCH_THRESHOLD
            
            mouse_x = np.interp(smoothed_ix, (FRAME_PADDING, w - FRAME_PADDING), (0, screen_w))
            mouse_y = np.interp(smoothed_iy, (FRAME_PADDING, h - FRAME_PADDING), (0, screen_h))

            pyautogui.moveTo(mouse_x, mouse_y)
            
            if pinch_active and not click_lock:
                pyautogui.click()
                print("¡CLIC!")
                click_lock = True
            
            if not pinch_active:
                click_lock = False

            color_index = (0, 0, 255) if pinch_active else (0, 255, 0)
            cv2.circle(frame, (smoothed_ix, smoothed_iy), 15, color_index, cv2.FILLED)
            cv2.circle(frame, (smoothed_tx, smoothed_ty), 10, (0, 255, 255), cv2.FILLED)
            
        else:
            smoothed_ix, smoothed_iy = None, None
            smoothed_tx, smoothed_ty = None, None

        # La visualización también consume recursos
        cv2.imshow('Controlador de Mouse Virtual', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()