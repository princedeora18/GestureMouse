import cv2
import mediapipe as mp
import pyautogui
import math


# Initialize MediaPipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False, 
    max_num_hands=1, 
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.7
)


# Drawing utilities to visualize landmarks
mp_drawing = mp.solutions.drawing_utils


# Get screen resolution 
screen_width, screen_height = pyautogui.size() 
camera_width, camera_height = 1280, 720


# Parameters for smoothing and pinch gesture detection
smoothing_factor = 5 
prev_cursor_x, prev_cursor_y = 0, 0
pinch_threshold = 0.08 
pinch_frame_count = 0
required_pinching_frames = 3 
is_pinched = False 

# Extra duration for pinch click accuracy
pinch_click_duration_frames = 5 


# Start capturing video
cap = cv2.VideoCapture(0)
cap.set(3, camera_width)  
cap.set(4, camera_height) 


def map_value(value, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


while True:
    success, frame = cap.read()
    if not success: 
        continue

    frame = cv2.flip(frame, 1) 
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        # Get thumb and index landmarks
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

        hand_x = (thumb_tip.x + index_tip.x) / 2
        hand_y = (thumb_tip.y + index_tip.y) / 2

        cursor_x = map_value(hand_x, 0.2, 0.8, 0, screen_width)
        cursor_y = map_value(hand_y, 0.2, 0.8, 0, screen_height)

        pinch_distance = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)

        smoothed_cursor_x = prev_cursor_x + (cursor_x - prev_cursor_x) / smoothing_factor
        smoothed_cursor_y = prev_cursor_y + (cursor_y - prev_cursor_y) / smoothing_factor

        pyautogui.moveTo(smoothed_cursor_x, smoothed_cursor_y)

        prev_cursor_x, prev_cursor_y = smoothed_cursor_x, smoothed_cursor_y

        if pinch_distance < pinch_threshold:
            pinch_frame_count += 1

            if pinch_frame_count >= pinch_click_duration_frames and not is_pinched:
                pyautogui.mouseDown()
                is_pinched = True
        else:
            if is_pinched:
                pyautogui.mouseUp()
                is_pinched = False
            pinch_frame_count = 0

        # Visual feedback
        if is_pinched:
            color = (0, 0, 255) 
            cv2.putText(frame, 'Dragging', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        else:
            color = (0, 255, 0)  

        thumb_coords = (int(thumb_tip.x * camera_width), int(thumb_tip.y * camera_height))
        index_coords = (int(index_tip.x * camera_width), int(index_tip.y * camera_height))
        cv2.line(frame, thumb_coords, index_coords, color, 3)

        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Gesture-Based Mouse Control', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if is_pinched:                     
            pyautogui.mouseUp()
        break


cap.release()
cv2.destroyAllWindows()
