from flask import Flask, render_template, Response, jsonify
import cv2
import time

from proctoring.face_detection import detect_faces
from proctoring.eye_head_detection import detect_head_movement
from proctoring.audio_detection import detect_background_voice
from proctoring.screen_monitor import detect_tab_switch
from proctoring.alert_engine import generate_alert, get_last_alert
from database.db import log_event, get_logs

app = Flask(__name__, template_folder=r"D:\Ai_Exam_Proctoring\frontend")

# =====================
# GLOBAL STATE
# =====================
exam_running = False
suspicion_score = 0
last_alert = ""


# =====================
# HOME PAGE
# =====================
@app.route("/")
def home():
    return render_template("index.html")


# =====================
# ADMIN LOGS
# =====================
@app.route("/admin/logs")
def admin_logs():
    logs = get_logs()
    return render_template("admin.html", logs=logs)


# =====================
# MJPEG VIDEO STREAM
# =====================
def generate_frames():
    global exam_running, suspicion_score, last_alert

    camera = cv2.VideoCapture(0)
    time.sleep(1)

    while True:
        if not exam_running:
            time.sleep(0.1)
            continue

        success, frame = camera.read()
        if not success:
            break

        # ---- FACE DETECTION ----
        face_count, _ = detect_faces(frame)
        if face_count > 1:
            suspicion_score += 2
            last_alert = "Multiple faces detected"
            generate_alert(last_alert)
            log_event(last_alert)

        # ---- HEAD / EYE MOVEMENT ----
        if detect_head_movement(frame):
            suspicion_score += 1
            last_alert = "Abnormal head movement"
            generate_alert(last_alert)
            log_event(last_alert)

        # ---- AUDIO DETECTION ----
        if detect_background_voice():
            suspicion_score += 1
            last_alert = "Background voice detected"
            generate_alert(last_alert)
            log_event(last_alert)

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )

    camera.release()


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# =====================
# START / STOP EXAM
# =====================
@app.route("/start_exam")
def start_exam():
    global exam_running, suspicion_score, last_alert
    exam_running = True
    suspicion_score = 0
    last_alert = ""
    return jsonify({"status": "started"})


@app.route("/stop_exam")
def stop_exam():
    global exam_running
    exam_running = False
    return jsonify({"status": "stopped"})


# =====================
# TAB SWITCH (REAL – FROM JS)
# =====================
@app.route("/tab_switched", methods=["POST"])
def tab_switched():
    global suspicion_score, last_alert

    if detect_tab_switch():
        suspicion_score += 1
        last_alert = "User switched browser tab"
        generate_alert(last_alert)
        log_event(last_alert)
        return jsonify({"status": "logged"})

    return jsonify({"status": "ignored"})


# =====================
# SCORE & ALERT APIs
# =====================
@app.route("/suspicion_score")
def get_score():
    return jsonify({"score": suspicion_score})


@app.route("/latest_alert")
def get_alert():


# =====================
# RUN SERVER
# =====================
if __name__ == "__main__":
    app.run(debug=True)
