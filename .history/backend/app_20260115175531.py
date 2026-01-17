from flask import Flask, render_template, Response, jsonify
import cv2
import time

from proctoring.face_detection import detect_faces
from proctoring.eye_head_detection import detect_head_movement
from proctoring.alert_engine import generate_alert
from database.db import log_event, get_logs

app = Flask(__name__, template_folder=r"D:\Ai_Exam_Proctoring\frontend")

# GLOBAL STATE
exam_running = False
suspicion_score = 0


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/admin/logs")
def admin_logs():
    logs = get_logs()
    return render_template("admin.html", logs=logs)


# 🔥 MJPEG STREAM (THIS IS THE FIX)
def generate_frames():
    global exam_running, suspicion_score

    camera = cv2.VideoCapture(0)   # ✅ OPEN CAMERA HERE
    time.sleep(1)

    while True:
        if not exam_running:
            time.sleep(0.1)
            continue

        success, frame = camera.read()
        if not success:
            break

        # FACE DETECTION
        face_count, _ = detect_faces(frame)
        if face_count > 1:
            suspicion_score += 2
            generate_alert("Multiple faces detected")
            log_event("Multiple faces detected")

        # HEAD MOVEMENT
        if detect_head_movement(frame):
            suspicion_score += 1
            generate_alert("Abnormal head movement")
            log_event("Abnormal head movement")

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


@app.route("/start_exam")
def start_exam():
    global exam_running, suspicion_score
    exam_running = True
    suspicion_score = 0
    return jsonify({"status": "started"})


@app.route("/stop_exam")
def stop_exam():
    global exam_running
    exam_running = False
    return jsonify({"status": "stopped"})


@app.route("/suspicion_score")
def get_score():
    return jsonify({"score": suspicion_score})


if __name__ == "__main__":
    app.run(debug=True)
