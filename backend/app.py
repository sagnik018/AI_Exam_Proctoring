from flask import Flask, render_template, Response, jsonify
import cv2
import time
import os
import threading
import sqlite3
from flask import Flask, render_template, request, jsonify, Response
import cv2
import numpy as np
from werkzeug.utils import secure_filename

# Import proctoring modules
from proctoring.face_detection import detect_faces
from proctoring.eye_head_detection import detect_head_movement
from proctoring.audio_detection import detect_background_voice
from proctoring.screen_monitor import detect_tab_switch
from proctoring.alert_engine import generate_alert, get_last_alert
from proctoring.screen_recording import start_screen_recording, stop_screen_recording, get_screenshot_count
from proctoring.face_recognition import initialize_face_recognition, register_new_user, verify_user_identity
from proctoring.alert_system import initialize_alert_system, create_severity_alert, get_alert_statistics, check_escalation_status
from proctoring.calibration import start_calibration_wizard, run_calibration_test, get_calibration_status, apply_optimal_settings
from proctoring.theme_manager import initialize_theme_manager, set_theme, get_current_theme, get_theme_css, get_available_themes
from database.db import log_event, get_logs

# Import screen recording
from PIL import ImageGrab
import datetime

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend"))
app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=FRONTEND_DIR, static_url_path="")

# =====================
# GLOBAL STATE
# =====================
exam_running = False
suspicion_score = 0
last_alert = ""

# New feature globals
screen_recording_active = False
calibration_in_progress = False
current_theme = "light"
alert_system_enabled = True

# =====================
# STREAMING / THREAD STATE
# =====================
_frame_lock = threading.Lock()
_latest_frame = None

_worker_started = False
_stop_event = threading.Event()

_detected_face_count = 0
_detected_head_suspicious = False

_audio_suspicious = False
_audio_last_check_time = 0.0

_last_event_time = {
    "multiple_faces": 0.0,
    "head_movement": 0.0,
    "background_voice": 0.0,
    "tab_switch": 0.0,
}


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
# SCREEN RECORDING ENDPOINTS
# =====================
@app.route("/api/screen_recording/toggle", methods=["POST"])
def toggle_screen_recording_api():
    global screen_recording_active
    if screen_recording_active:
        stop_screen_recording()
        screen_recording_active = False
        log_event("Screen recording stopped")
    else:
        start_screen_recording()
        screen_recording_active = True
        log_event("Screen recording started")
    return jsonify({"status": "success", "recording": screen_recording_active})

@app.route("/api/screen_recording/stop", methods=["POST"])
def stop_screen_recording_api():
    global screen_recording_active
    if screen_recording_active:
        stop_screen_recording()
        screen_recording_active = False
        log_event("Screen recording stopped")
    return jsonify({"status": "success", "recording": screen_recording_active})

@app.route("/api/screen_recording/status")
def screen_recording_status():
    screenshot_count = get_screenshot_count()
    return jsonify({
        "recording": screen_recording_active,
        "screenshots_taken": screenshot_count
    })

# =====================
# FACE RECOGNITION ENDPOINTS
# =====================
@app.route("/api/face_recognition/verify_quick", methods=["POST"])
def verify_face_quick_api():
    global _latest_frame
    if _latest_frame is None:
        return jsonify({"status": "error", "message": "No camera feed available"})
    
    verification_result = quick_face_verification(_latest_frame)
    
    if verification_result['verified']:
        log_event(f"Face verified: {verification_result.get('name', 'Unknown')}")
    
    return jsonify({
        "status": "success",
        "verification": verification_result
    })

@app.route("/api/face_recognition/register", methods=["POST"])
def register_face_api():
    try:
        # This would normally get image from request
        # For now, return instructions
        return jsonify({
            "status": "info",
            "message": "Face registration requires image upload endpoint",
            "instructions": "Use face registration with proper image capture"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/face_recognition/verify")
def verify_face_api():
    global _latest_frame
    if _latest_frame is None:
        return jsonify({"status": "error", "message": "No camera feed available"})
    
    verification_result = verify_user_identity(_latest_frame)
    
    if verification_result['unauthorized_present']:
        create_severity_alert('unauthorized_face', 'Unauthorized person detected')
        log_event("Unauthorized face detected")
        suspicion_score = globals().get('suspicion_score', 0) + 5
    
    return jsonify({
        "status": "success",
        "verification": verification_result,
        "authorized": verification_result['authorized_present']
    })

# =====================
# ALERT SYSTEM ENDPOINTS
# =====================
@app.route("/api/alerts/statistics")
def alert_statistics_api():
    stats = get_alert_statistics()
    return jsonify({"status": "success", "statistics": stats})

@app.route("/api/alerts/recent")
def recent_alerts_api():
    count = request.args.get('count', 10, type=int)
    alerts = initialize_alert_system().get_recent_alerts(count)
    return jsonify({"status": "success", "alerts": alerts})

@app.route("/api/alerts/escalation/<alert_type>")
def check_escalation_api(alert_type):
    escalated = check_escalation_status(alert_type)
    return jsonify({"status": "success", "escalated": escalated})

# =====================
# CALIBRATION ENDPOINTS
# =====================
@app.route("/api/calibration/start", methods=["POST"])
def start_calibration_api():
    global calibration_in_progress
    if not calibration_in_progress:
        result = start_calibration_wizard()
        calibration_in_progress = True
        log_event("Calibration wizard started")
    return jsonify({"status": "success", "calibration": result})

@app.route("/api/calibration/test/<step>", methods=["POST"])
def run_calibration_test_api(step):
    global _latest_frame
    frame = _latest_frame if _latest_frame is not None else None
    
    result = run_calibration_test(step, frame)
    return jsonify({"status": "success", "step": step, "result": result})

@app.route("/api/calibration/next", methods=["POST"])
def calibration_next_step_api():
    global calibration_in_progress
    if calibration_in_progress:
        result = calibration_wizard.next_step()
        if result.get('status') == 'completed':
            calibration_in_progress = False
            log_event("Calibration completed")
    return jsonify({"status": "success", "result": result})

@app.route("/api/calibration/status")
def calibration_status_api():
    status = get_calibration_status()
    return jsonify({"status": "success", "calibration": status})

@app.route("/api/calibration/settings")
def calibration_settings_api():
    settings = apply_optimal_settings()
    return jsonify({"status": "success", "settings": settings})

# =====================
# THEME ENDPOINTS
# =====================
@app.route("/api/themes")
def available_themes_api():
    themes = get_available_themes()
    current = get_current_theme()
    css = get_theme_css()
    
    return jsonify({
        "status": "success",
        "current_theme": current,
        "available_themes": themes,
        "css": css
    })

@app.route("/api/themes/set/<theme_name>", methods=["POST"])
def set_theme_api(theme_name):
    success = set_theme(theme_name)
    if success:
        global current_theme
        current_theme = theme_name
        log_event(f"Theme changed to {theme_name}")
    
    return jsonify({
        "status": "success" if success else "error",
        "theme": theme_name,
        "current_theme": get_current_theme()
    })

@app.route("/themes.css")
def theme_css_endpoint():
    css = get_theme_css()
    return Response(css, mimetype='text/css')


# =====================
# MJPEG VIDEO STREAM
# =====================
def _ensure_workers_started():
    global _worker_started

    if _worker_started:
        return

    _worker_started = True
    _stop_event.clear()

    threading.Thread(target=_capture_worker, daemon=True).start()
    threading.Thread(target=_detection_worker, daemon=True).start()
    threading.Thread(target=_audio_worker, daemon=True).start()


def _capture_worker():
    global _latest_frame

    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    except Exception:
        cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass

    time.sleep(0.2)

    try:
        while not _stop_event.is_set():
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.01)
                continue
            with _frame_lock:
                _latest_frame = frame
    finally:
        cap.release()


def _detection_worker():
    global suspicion_score, last_alert
    global _detected_face_count, _detected_head_suspicious

    event_cooldown_seconds = {
        "multiple_faces": 3.0,
        "head_movement": 2.0,
    }

    frame_index = 0
    detection_every_n_frames = 3

    head_suspicious_streak = 0
    head_suspicious_required = 3

    no_face_streak = 0
    multiple_faces_streak = 0
    face_streak_required = 3
    last_face_seen_time = 0.0
    face_grace_seconds = 1.5

    while not _stop_event.is_set():
        if not exam_running:
            _detected_face_count = 0
            _detected_head_suspicious = False
            time.sleep(0.05)
            continue

        with _frame_lock:
            frame = None if _latest_frame is None else _latest_frame.copy()

        if frame is None:
            time.sleep(0.01)
            continue

        if frame_index % detection_every_n_frames == 0:
            try:
                face_count, _ = detect_faces(frame)
                now = time.time()

                if face_count == 0:
                    no_face_streak += 1
                    multiple_faces_streak = 0
                else:
                    no_face_streak = 0
                    last_face_seen_time = now

                if face_count > 1:
                    multiple_faces_streak += 1
                else:
                    multiple_faces_streak = 0

                # Debounced face count for UI:
                # - keep showing previous face state for a short grace period
                # - only show 0 or >1 after consecutive confirmations
                if no_face_streak >= face_streak_required:
                    _detected_face_count = 0
                elif multiple_faces_streak >= face_streak_required:
                    _detected_face_count = face_count
                else:
                    if now - last_face_seen_time <= face_grace_seconds:
                        _detected_face_count = 1
                    else:
                        _detected_face_count = face_count

                if multiple_faces_streak >= face_streak_required:
                    if now - _last_event_time["multiple_faces"] >= event_cooldown_seconds["multiple_faces"]:
                        _last_event_time["multiple_faces"] = now
                        suspicion_score += 2
                        last_alert = "Multiple faces detected"
                        generate_alert(last_alert)
                        log_event(last_alert)
            except Exception:
                pass

            try:
                head_suspicious = detect_head_movement(frame)
                if head_suspicious:
                    head_suspicious_streak += 1
                else:
                    head_suspicious_streak = 0

                _detected_head_suspicious = head_suspicious_streak >= head_suspicious_required
                if _detected_head_suspicious:
                    now = time.time()
                    if now - _last_event_time["head_movement"] >= event_cooldown_seconds["head_movement"]:
                        _last_event_time["head_movement"] = now
                        suspicion_score += 1
                        last_alert = "Abnormal head movement"
                        generate_alert(last_alert)
                        log_event(last_alert)
            except Exception:
                pass

        frame_index += 1
        time.sleep(0.001)


def _audio_worker():
    global suspicion_score, last_alert
    global _audio_suspicious, _audio_last_check_time

    event_cooldown_seconds = 6.0

    audio_check_interval_seconds = 6.0

    while not _stop_event.is_set():
        if not exam_running:
            _audio_suspicious = False
            time.sleep(0.2)
            continue

        now = time.time()
        if now - _audio_last_check_time < audio_check_interval_seconds:
            time.sleep(0.1)
            continue

        _audio_last_check_time = now
        detected = detect_background_voice()
        _audio_suspicious = detected
        if detected:
            now = time.time()
            if now - _last_event_time["background_voice"] >= event_cooldown_seconds:
                _last_event_time["background_voice"] = now
                suspicion_score += 1
                last_alert = "Background voice detected"
                generate_alert(last_alert)
                log_event(last_alert)


def generate_frames():
    _ensure_workers_started()

    target_fps = 30.0
    min_frame_time = 1.0 / target_fps
    last_sent = 0.0

    while True:
        now = time.time()
        sleep_for = min_frame_time - (now - last_sent)
        if sleep_for > 0:
            time.sleep(sleep_for)
        last_sent = time.time()

        with _frame_lock:
            frame = None if _latest_frame is None else _latest_frame.copy()
            face_count = _detected_face_count
            head_suspicious = _detected_head_suspicious
            audio_suspicious = _audio_suspicious

        if frame is None:
            time.sleep(0.02)
            continue

        if not exam_running:
            cv2.putText(
                frame,
                "Click Start Exam",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
        else:
            if face_count == 1:
                cv2.putText(
                    frame,
                    "Face detected - OK",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )
            elif face_count == 0:
                cv2.putText(
                    frame,
                    "No face detected",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )
            elif face_count > 1:
                cv2.putText(
                    frame,
                    "Multiple faces detected",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

            if head_suspicious:
                cv2.putText(
                    frame,
                    "Abnormal head movement",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

            if audio_suspicious:
                cv2.putText(
                    frame,
                    "Background voice detected",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

        ret, buffer = cv2.imencode(
            ".jpg",
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 75],
        )
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


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

    if not exam_running:
        return jsonify({"status": "ignored"})

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
    return jsonify(get_last_alert())


# =====================
# RUN SERVER
# =====================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, threaded=True)
