import cv2
import mediapipe as mp
import pyautogui
import math



# Initialize MediaPipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,         # Real-time tracking (not on static images)
    max_num_hands=1,                 # Track only one hand at a time
    min_detection_confidence=0.7,    # Minimum confidence for detecting a hand
    min_tracking_confidence=0.7      # Minimum confidence for tracking a hand
)




# Drawing utilities to visualize landmarks and hand connections
mp_drawing = mp.solutions.drawing_utils

# Get screen resolution and set camera resolution for better alignment
screen_width, screen_height = pyautogui.size()  # Get screen width and height
camera_width, camera_height = 1280, 720         # Set camera resolution

# Parameters for cursor smoothing and pinch gesture detection
smoothing_factor = 5                # Adjusts how smoothly the cursor follows the hand
prev_cursor_x, prev_cursor_y = 0, 0  # Previous cursor position (used for smoothing)
pinch_threshold = 0.08             # Threshold to detect pinch between thumb and index finger
pinch_frame_count = 0               # To count how many frames the pinch gesture lasts
required_pinching_frames = 3        # How many frames of pinch are needed before action
is_pinched = False                 # Boolean flag to track if pinch gesture is active


# Extra duration for pinch click accuracy
pinch_click_duration_frames = 5  # Number of frames pinch must last for a click


# Start capturing video using the default webcam (index 0)
 cap = cv2.VideoCapture(0)
 cap.set(3, camera_width)  # Set camera width
 cap.set(4, camera_height) # Set camera height

  # Function to map a value from one range to another (for cursor mapping)

def map_value(value, in_min, in_max, out_min, out_max):

    """Maps a value from one range to another"""
    
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

  # Capture frames in a loop
while True:
    success, frame = cap.read()
    if not success:
        continue

    # Flip the frame horizontally to mimic natural interaction (mirror effect)
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert the frame to RGB for MediaPipe processing
    results = hands.process(frame_rgb)  # Process the frame with MediaPipe to detect hand landmarks

    
    # If hand landmarks are detected
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        # Get the thumb and index finger landmarks for tracking pinch gesture
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

        # Calculate the midpoint between thumb and index finger for cursor movement
        hand_x = (thumb_tip.x + index_tip.x) / 2
        hand_y = (thumb_tip.y + index_tip.y) / 2

        
        # Map the hand position to screen coordinates for cursor movement
        cursor_x = map_value(hand_x, 0.2, 0.8, 0, screen_width)
        cursor_y = map_value(hand_y, 0.2, 0.8, 0, screen_height)

        # Calculate the distance between thumb and index to detect pinch
        pinch_distance = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)

        
        # Smooth cursor movement for a more natural experience
        smoothed_cursor_x = prev_cursor_x + (cursor_x - prev_cursor_x) / smoothing_factor
        smoothed_cursor_y = prev_cursor_y + (cursor_y - prev_cursor_y) / smoothing_factor

        # Move the mouse cursor using pyautogui based on the hand's position
        pyautogui.moveTo(smoothed_cursor_x, smoothed_cursor_y)
        
        prev_cursor_x, prev_cursor_y = smoothed_cursor_x, smoothed_cursor_y

        # Pinch detection logic
        if pinch_distance < pinch_threshold:
            pinch_frame_count += 1
        
            # Wait until pinch gesture is stable for a few frames before simulating a click
            
            if pinch_frame_count >= pinch_click_duration_frames and not is_pinched:
                pyautogui.mouseDown()  # Simulate mouse click down
                is_pinched = True
        else:
            if is_pinched:
                pyautogui.mouseUp()  # Release mouse click if pinch is not detected anymore
                is_pinched = False
            pinch_frame_count = 0  # Reset pinch frame count when pinch is not detected

        # Provide visual feedback based on pinch state
        
        if is_pinched:
            color = (0, 0, 255)  # Red color when dragging (pinch active)
            cv2.putText(frame, 'Dragging', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        else:
            color = (0, 255, 0)  # Green color when no pinch detected

        # Draw a line between thumb and index for visual feedback
        
        thumb_coords = (int(thumb_tip.x * camera_width), int(thumb_tip.y * camera_height))
        index_coords = (int(index_tip.x * camera_width), int(index_tip.y * camera_height))
        cv2.line(frame, thumb_coords, index_coords, color, 3)

        # Draw landmarks to show detected points
        
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Show the frame with gesture control
    cv2.imshow('Gesture-Based Mouse Control', frame)

    # Exit the loop if 'q' is pressed
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        if is_pinched:                     # Ensure mouse is released if still pressed
            pyautogui.mouseUp()
        break


# Release the video capture and close the display window

cap.release()
cv2.destroyAllWindows()
