from flask import Flask
import cv2
import time

from proctoring.face_detection import detect_faces
from proctoring.eye_head_detection import detect_head_movement
from proctoring.audio_detection import detect_background_voice
from proctoring.screen_monitor import detect_tab_switch
from proctoring.alert_engine import generate_alert
from database.db import log_event

app = Flask(__name__)

# Health check / status route
@app.route("/")
def home():
    return "AI-Based Online Exam Proctoring System Backend is Running"

# Main proctoring route (called from frontend)
@app.route("/start_exam")
def start_exam():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return "Webcam not accessible", 500

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Face detection
        face_count, _ = detect_faces(frame)
        if face_count > 1:
            generate_alert("Multiple faces detected")
            log_event("Multiple faces detected")

        # 2. Head / eye movement detection
        if detect_head_movement(frame):
            generate_alert("Abnormal head movement")
            log_event("Abnormal head movement")

        # 3. Background voice detection
        if detect_background_voice():
            generate_alert("Background voice detected")
            log_event("Background voice detected")

        # 4. Tab switching detection
        if detect_tab_switch(time.time()):
            generate_alert("Possible tab switching")
            log_event("Possible tab switching")

        # Press Q to stop proctoring
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return "AI Proctoring Session Ended"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
