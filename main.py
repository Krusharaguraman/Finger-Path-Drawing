import cv2
import mediapipe as mp
import math

# Initialize MediaPipe hands and drawing utilities
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Initialize OpenCV
cap = cv2.VideoCapture(0)

# Variables to track drawing state
drawing_path = []  # Stores the drawing path (a list of points)
current_line = []  # Stores the points of the current line

# You can adjust this threshold value to better suit your needs
FINGER_OPEN_THRESHOLD = 0.15  # Increase this value to make the detection stricter

def is_index_finger_open(landmarks):
    # Calculate the distance between thumb (landmark 4) and index finger tip (landmark 8)
    thumb_tip = landmarks.landmark[4]
    index_tip = landmarks.landmark[8]
    
    # Calculate Euclidean distance between thumb tip and index finger tip
    distance = math.sqrt((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2)
    
    # Index finger is considered open if the distance is larger than the threshold
    return distance > FINGER_OPEN_THRESHOLD  # You can adjust this threshold for sensitivity

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the image for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Draw landmarks on the image
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            # Draw all the landmarks on the hand
            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

            # Check if the index finger is open
            if is_index_finger_open(landmarks):
                # Get the position of the index finger tip (landmark 8)
                index_finger_tip = landmarks.landmark[8]
                x = int(index_finger_tip.x * frame.shape[1])
                y = int(index_finger_tip.y * frame.shape[0])

                # Start a new line if the previous hand was closed (no drawing in progress)
                if not current_line:
                    current_line.append((x, y))  # Start a new line
                else:
                    # If index finger is open, keep adding to the current line
                    current_line.append((x, y))
            else:
                # If index finger is closed, finalize the current line and add it to the drawing path
                if current_line:
                    drawing_path.append(current_line)
                    current_line = []  # Reset for next line

    # Draw all completed lines
    for line in drawing_path:
        for i in range(1, len(line)):
            cv2.line(frame, line[i - 1], line[i], (0, 0, 0), 2)

    # Draw the current line (if the index finger is open)
    if current_line:
        for i in range(1, len(current_line)):
            cv2.line(frame, current_line[i - 1], current_line[i], (255, 255, 255), 2)

    # Display the frame with the drawn finger path
    cv2.imshow('Finger Path Drawing', frame)

    # Check for 'q' to quit and 'r' to reset drawing
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('r'):  # Press 'r' to reset drawing
        drawing_path = []  # Clear all previous drawings
        current_line = []  # Clear the current line

cap.release()
cv2.destroyAllWindows()
