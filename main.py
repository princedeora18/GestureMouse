import cv2
import mediapipe as mp
import pyautogui
import math

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Screen and camera settings
screen_w, screen_h = pyautogui.size()
cam_w, cam_h = 1280, 720

# Smoothing and pinch detection parameters
smoothening = 5
plocX, plocY = 0, 0
pinch_threshold = 0.08  # Normalized distance threshold for pinch
pinch_frames = 0
pinch_frames_required = 3
is_pinched = False

# Additional Pinch Click parameters for accuracy
pinch_duration_frames = 5  # Frames to maintain pinch before registering click

cap = cv2.VideoCapture(0)
cap.set(3, cam_w)
cap.set(4, cam_h)

def map_value(value, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

while True:
    success, img = cap.read()
    if not success:
        continue

    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        # Get thumb and index finger landmarks
        thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

        # Convert landmarks to screen coordinates
        hand_x = (thumb.x + index.x) / 2
        hand_y = (thumb.y + index.y) / 2

        # Map hand position to screen coordinates
        cursor_x = map_value(hand_x, 0.2, 0.8, 0, screen_w)
        cursor_y = map_value(hand_y, 0.2, 0.8, 0, screen_h)

        # Calculate normalized distance between thumb and index
        pinch_distance = math.hypot(thumb.x - index.x, thumb.y - index.y)

        # Smooth cursor movement
        clocX = plocX + (cursor_x - plocX) / smoothening
        clocY = plocY + (cursor_y - plocY) / smoothening

        # Update cursor position
        pyautogui.moveTo(clocX, clocY)
        plocX, plocY = clocX, clocY

        # Pinch detection logic
        if pinch_distance < pinch_threshold:
            pinch_frames += 1
            # Wait until pinch is stable for a few frames before registering click
            if pinch_frames >= pinch_duration_frames and not is_pinched:
                pyautogui.mouseDown()
                is_pinched = True
        else:
            if is_pinched:
                pyautogui.mouseUp()
                is_pinched = False
            pinch_frames = 0

        # Visual feedback on the current pinch state
        if is_pinched:
            color = (0, 0, 255)  # Red when pinched
            cv2.putText(img, 'Dragging', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        else:
            color = (0, 255, 0)  # Green when not pinched

        # Draw connection line between thumb and index
        thumb_px = (int(thumb.x * cam_w), int(thumb.y * cam_h))
        index_px = (int(index.x * cam_w), int(index.y * cam_h))
        cv2.line(img, thumb_px, index_px, color, 3)

        # Draw hand landmarks
        mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Apple-Style Gesture Control', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        if is_pinched:  # Release mouse if still pressed
            pyautogui.mouseUp()
        break

cap.release()
cv2.destroyAllWindows()
