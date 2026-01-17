# backend/app.py
from flask import Flask
import cv2, time

from proctoring.face_detection import detect_faces
from proctoring.audio_detection import detect_background_voice
from proctoring.alert_engine import generate_alert
from database.db import log_event

app = Flask(__name__)

@app.route("/start_exam")
def start_exam():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        face_count, _ = detect_faces(frame)
        if face_count > 1:
            generate_alert("Multiple Faces Detected")
            log_event("Multiple Faces Detected")

        if detect_background_voice():
            generate_alert("Background Voice Detected")
            log_event("Background Voice Detected")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    return "Exam Monitoring Ended"

if __name__ == "__main__":
    app.run(debug=True)
