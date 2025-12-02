import cv2
import mediapipe as mp
from datetime import datetime
import time
from config import TEACHER_PHONE, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, NOTIFICATION_COOLDOWN
import threading
from twilio.rest import Client

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
LEFT_IRIS = [468, 469, 470, 471, 472]
RIGHT_IRIS = [473, 474, 475, 476, 477]
MOUTH_TOP = [13]
MOUTH_BOTTOM = [14]

last_notification_time = {}

def send_notification(status, face_num):
    current_time = time.time()
    print(f"[DEBUG] Status detected: {status} for Face {face_num}")
    
    if face_num in last_notification_time:
        time_since_last = current_time - last_notification_time[face_num]
        if time_since_last < NOTIFICATION_COOLDOWN:
            print(f"[DEBUG] Cooldown active. Wait {NOTIFICATION_COOLDOWN - time_since_last:.0f}s more")
            return
    
    print(f"[INFO] Sending WhatsApp notification for Face {face_num}: {status}")
    
    def send_sms():
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            message_body = f"""Student Attention Alert
Status: {status}
Time: {datetime.now().strftime('%H:%M:%S')}
Student ID: {face_num}"""
            
            message = client.messages.create(
                from_=TWILIO_PHONE_NUMBER,
                body=message_body,
                to=TEACHER_PHONE
            )
            
            print(f"[SUCCESS] SMS sent for Face {face_num}: {status} (SID: {message.sid})")
        except Exception as e:
            print(f"[ERROR] Failed to send SMS: {e}")
    
    last_notification_time[face_num] = current_time
    threading.Thread(target=send_sms, daemon=True).start()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
status = "Listening Sincerely"

with mp_face_mesh.FaceMesh(max_num_faces=4, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            for face_num, face_landmarks in enumerate(results.multi_face_landmarks, 1):
                landmarks = face_landmarks.landmark
                
                # Eye aspect ratio for closed eyes
                def ear(eye_indices):
                    coords = [(landmarks[i].x * w, landmarks[i].y * h) for i in eye_indices]
                    vertical = abs(coords[1][1] - coords[5][1]) + abs(coords[2][1] - coords[4][1])
                    horizontal = abs(coords[0][0] - coords[3][0])
                    return vertical / (2.0 * horizontal) if horizontal > 0 else 0
                
                left_ear = ear(LEFT_EYE)
                right_ear = ear(RIGHT_EYE)
                avg_ear = (left_ear + right_ear) / 2
                
                # Iris position for looking away
                left_iris_x = sum([landmarks[i].x for i in LEFT_IRIS]) / len(LEFT_IRIS)
                left_eye_x = sum([landmarks[i].x for i in LEFT_EYE]) / len(LEFT_EYE)
                right_iris_x = sum([landmarks[i].x for i in RIGHT_IRIS]) / len(RIGHT_IRIS)
                right_eye_x = sum([landmarks[i].x for i in RIGHT_EYE]) / len(RIGHT_EYE)
                
                iris_deviation = (abs(left_iris_x - left_eye_x) + abs(right_iris_x - right_eye_x)) / 2
                
                # Mouth opening detection
                mouth_top_y = landmarks[13].y * h
                mouth_bottom_y = landmarks[14].y * h
                mouth_opening = abs(mouth_bottom_y - mouth_top_y)
                
                # Head tilt (nose vs forehead)
                nose_tip_y = landmarks[1].y
                forehead_y = landmarks[10].y
                head_tilt = nose_tip_y - forehead_y
                
                # Head rotation (left/right) - check nose position relative to face center
                nose_x = landmarks[1].x
                left_cheek_x = landmarks[234].x
                right_cheek_x = landmarks[454].x
                face_center_x = (left_cheek_x + right_cheek_x) / 2
                head_rotation = abs(nose_x - face_center_x)
                
                # Priority: Sleeping > Distracted > Speaking > Turning > Using Mobile > Listening
                if avg_ear < 0.15:
                    status = "Sleeping"
                    color = (128, 0, 128)  # Purple
                    send_notification(status, face_num)
                elif head_tilt > 0.25:  # Only heavily down is distracted
                    status = "Distracted"
                    color = (0, 0, 255)  # Red
                    send_notification(status, face_num)
                elif mouth_opening > 15:
                    status = "Speaking"
                    color = (255, 255, 0)  # Cyan
                elif head_rotation > 0.03:
                    status = "Turning"
                    color = (255, 128, 0)  # Blue
                elif iris_deviation > 0.02:
                    status = "Using Mobile"
                    color = (0, 165, 255)  # Orange
                else:
                    # Listening: eyes straight, mouth closed, face straight or slightly down
                    status = "Listening Sincerely"
                    color = (0, 255, 0)  # Green
                
                # Simplified drawing - only contours, no full mesh
                mp_drawing.draw_landmarks(
                    frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS,
                    mp_drawing.DrawingSpec(color=(255, 200, 150), thickness=1, circle_radius=0),
                    mp_drawing.DrawingSpec(color=(255, 200, 150), thickness=1))
                
                # Display status near each face
                face_x = int(landmarks[1].x * w)
                face_y = int(landmarks[10].y * h) - 30
                cv2.putText(frame, status, (face_x - 100, face_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        cv2.imshow('Attention Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
