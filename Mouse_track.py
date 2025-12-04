import cv2
import mediapipe as mp
import math
import pyautogui # ¡La nueva librería para controlar el mouse!
import numpy as np # Necesaria para el mapeo de coordenadas

# --- CONFIGURACIÓN GENERAL ---
alpha = 0.5 # Un poco más de respuesta para el control del mouse
PINCH_THRESHOLD = 20
FRAME_PADDING = 100 # Un borde de 100 píxeles para no tener que llegar a los bordes del video

# --- ESTADO DEL CONTROLADOR ---
click_lock = False # Bloqueo para evitar múltiples clics en un solo pellizco

# --- INICIALIZACIÓN DE LIBRERÍAS ---
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0)

# Obtener las dimensiones de la pantalla del monitor (¡solo una vez!)
screen_w, screen_h = pyautogui.size()
print(f"Dimensiones del monitor detectadas: {screen_w}x{screen_h}")

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
        results = hands.process(image_rgb)
        
        # Dibuja el área de control en el video
        cv2.rectangle(frame, (FRAME_PADDING, FRAME_PADDING), (w - FRAME_PADDING, h - FRAME_PADDING), (255, 255, 0), 2)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # 1. OBTENER Y SUAVIZAR PUNTOS
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

            # 2. DETECTAR PELLIZCO
            distance = math.dist((smoothed_ix, smoothed_iy), (smoothed_tx, smoothed_ty))
            pinch_active = distance < PINCH_THRESHOLD
            
            # --- 3. LÓGICA DE CONTROL DEL MOUSE ---
            
            # Mapeo de coordenadas: convierte la posición del dedo a la del monitor
            # Usamos np.interp para una conversión lineal y suave
            mouse_x = np.interp(smoothed_ix, (FRAME_PADDING, w - FRAME_PADDING), (0, screen_w))
            mouse_y = np.interp(smoothed_iy, (FRAME_PADDING, h - FRAME_PADDING), (0, screen_h))

            # Mover el mouse
            pyautogui.moveTo(mouse_x, mouse_y)
            
            # Lógica de Clic
            if pinch_active and not click_lock:
                pyautogui.click()
                print("¡CLIC!")
                click_lock = True # Bloqueamos para no hacer más clics
            
            if not pinch_active:
                click_lock = False # Desbloqueamos cuando se suelta el pellizco

            # --- 4. DIBUJAR FEEDBACK ---
            
            # Cambia el color del círculo del índice si hace clic
            color_index = (0, 0, 255) if pinch_active else (0, 255, 0)
            cv2.circle(frame, (smoothed_ix, smoothed_iy), 15, color_index, cv2.FILLED)
            cv2.circle(frame, (smoothed_tx, smoothed_ty), 10, (0, 255, 255), cv2.FILLED)
            
        else:
            smoothed_ix, smoothed_iy = None, None
            smoothed_tx, smoothed_ty = None, None

        cv2.imshow('Controlador de Mouse Virtual', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()