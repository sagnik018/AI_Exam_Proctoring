from flask import Flask, render_template, Response, jsonify
import cv2
import time

from proctoring.face_detection import detect_faces
from proctoring.eye_head_detection import detect_head_movement
from proctoring.audio_detection import detect_background_voice
from proctoring.screen_monitor import detect_tab_switch
from proctoring.alert_engine import generate_alert
from database.db import log_event, get_logs

# Flask app (frontend folder unchanged)
app = Flask(__name__, template_folder=r"D:\Ai_Exam_Proctoring\frontend")

# =========================
# GLOBAL CONTROL VARIABLES
# =========================
camera = None
exam_running = False
suspicion_score = 0


# =========================
# HOME PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# ADMIN LOGS PAGE
# =========================
@app.route("/admin/logs")
def admin_logs():
    logs = get_logs()
    return render_template("admin.html", logs=logs)


# =========================
# VIDEO FRAME GENERATOR
# =========================
def generate_frames():
    global camera, exam_running, suspicion_score

    while True:
        # Keep stream alive even if exam not started
        if not exam_running or camera is None:
            time.sleep(0.1)
            continue

        success, frame = camera.read()
        if not success:
            break

        # ---- Face Detection ----
        face_count, _ = detect_faces(frame)
        if face_count > 1:
            suspicion_score += 2
            generate_alert("Multiple faces detected")
            log_event("Multiple faces detected")

        # ---- Head Movement ----
        if detect_head_movement(frame):
            suspicion_score += 1
            generate_alert("Abnormal head movement")
            log_event("Abnormal head movement")

        # ---- Audio Detection (lightweight) ----
        if detect_background_voice():
            suspicion_score += 1
            generate_alert("Background voice detected")
            log_event("Background voice detected")

        # ---- Tab Switch Detection ----
        if detect_tab_switch(time.time()):
            suspicion_score += 1
            generate_alert("Possible tab switching")
            log_event("Possible tab switching")

        # Encode frame
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


# =========================
# VIDEO STREAM ROUTE
# =========================
@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# =========================
# START EXAM
# =========================
@app.route("/start_exam")
def start_exam():
    global camera, exam_running, suspicion_score

    if not exam_running:
        camera = cv2.VideoCapture(0)
        exam_running = True
        suspicion_score = 0

    return jsonify({"status": "started"})


# =========================
# STOP EXAM
# =========================
@app.route("/stop_exam")
def stop_exam():
    global camera, exam_running

    exam_running = False
    if camera:
        camera.release()
        camera = None

    cv2.destroyAllWindows()
    return jsonify({"status": "stopped"})


# =========================
# SUSPICION SCORE API
# =========================
@app.route("/suspicion_score")
def get_score():
    return jsonify({"score": suspicion_score})


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)
