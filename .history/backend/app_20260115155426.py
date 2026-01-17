from flask import Flask, render_template, Response, jsonify
import cv2
import time
import threading

from proctoring.face_detection import detect_faces
from proctoring.eye_head_detection import detect_head_movement
from proctoring.audio_detection import detect_background_voice
from proctoring.screen_monitor import detect_tab_switch
from proctoring.alert_engine import generate_alert
from database.db import log_event

# Flask app (frontend folder remains unchanged)
app = Flask(__name__, template_folder="../frontend")


# GLOBAL CONTROL VARIABLES
camera = None
exam_running = False
suspicion_score = 0

# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")

# VIDEO FRAME GENERATOR
def generate_frames():
    global camera, exam_running, suspicion_score

    while exam_running:
        success, frame = camera.read()
        if not success:
            break

        # Face detection
        face_count, _ = detect_faces(frame)
        if face_count > 1:
            suspicion_score += 2
            generate_alert("Multiple faces detected")
            log_event("Multiple faces detected")

        # Head movement detection
        if detect_head_movement(frame):
            suspicion_score += 1
            generate_alert("Abnormal head movement")
            log_event("Abnormal head movement")

        # Encode frame for browser
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )

# VIDEO STREAM ROUTE
@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# START EXAM
def start_exam():
    global camera, exam_running, suspicion_score

    if not exam_running:
        camera = cv2.VideoCapture(0)
        exam_running = True
        suspicion_score = 0

    return jsonify({"status": "started"})

# STOP EXAM
@app.route("/stop_exam")
def stop_exam():
    global camera, exam_running

    exam_running = False
    if camera:
        camera.release()

    cv2.destroyAllWindows()
    return jsonify({"status": "stopped"})

# SUSPICION SCORE API
@app.route("/suspicion_score")
def get_score():
    return jsonify({"score": suspicion_score})



# RUN SERVER
if __name__ == "__main__":
    app.run(debug=True)
