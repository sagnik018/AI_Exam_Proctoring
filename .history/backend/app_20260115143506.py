from flask import Flask
import cv2
import time
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from proctoring.face_detection import detect_faces
from proctoring.eye_head_detection import detect_head_movement
from proctoring.audio_detection import detect_background_voice
from proctoring.screen_monitor import detect_tab_switch
from proctoring.alert_engine import generate_alert
from database.db import log_event

app = Flask(__name__)

@app.route("/start_exam")
def start_exam():
    cap = cv2.VideoCapture(0)
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Face detection
        face_count, _ = detect_faces(frame)
        if face_count > 1:
            generate_alert("Multiple faces detected")
            log_event("Multiple faces detected")

        # Head movement
        if detect_head_movement(frame):
            generate_alert("Abnormal head movement")
            log_event("Abnormal head movement")

        # Audio detection
        if detect_background_voice():
            generate_alert("Background voice detected")
            log_event("Background voice detected")

        # Tab switching simulation
        if detect_tab_switch(time.time()):
            generate_alert("Possible tab switching")
            log_event("Possible tab switching")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return "AI Proctoring Session Ended"

if __name__ == "__main__":
    app.run(debug=True)
