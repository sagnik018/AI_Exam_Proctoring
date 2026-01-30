from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, send_from_directory
from flask_cors import CORS
import cv2
import time
import os
import threading
import sqlite3
import numpy as np
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Import proctoring modules
from proctoring.face_detection import detect_faces
from proctoring.eye_head_detection import detect_head_movement
from proctoring.audio_detection import detect_background_voice
from proctoring.screen_monitor import detect_tab_switch
from proctoring.alert_engine import generate_alert, get_last_alert, clear_alert_queue
from proctoring.screen_recording import start_screen_recording, stop_screen_recording, get_screenshot_count
from proctoring.face_recognition import initialize_face_recognition, register_new_user, verify_user_identity, quick_face_verification
from proctoring.alert_system import initialize_alert_system, create_severity_alert, get_alert_statistics, check_escalation_status
from proctoring.calibration import start_calibration_wizard, run_calibration_test, get_calibration_status, apply_optimal_settings
from proctoring.theme_manager import initialize_theme_manager, set_theme, get_current_theme, get_theme_css, get_available_themes
from database.db import log_event, get_logs

# Import screen recording
from PIL import ImageGrab
import datetime

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend"))
BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.abspath(os.path.join(BACKEND_DIR, "exam_logs.db"))

app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=FRONTEND_DIR, static_url_path="")

# =====================
# INITIALIZE CORS
# =====================
CORS(app, resources={r"/api/*": {"origins": "*"}, r"/video_feed": {"origins": "*"}, 
                     r"/start_exam": {"origins": "*"}, r"/stop_exam": {"origins": "*"},
                     r"/submit_details": {"origins": "*"}, r"/tab_switched": {"origins": "*"},
                     r"/suspicion_score": {"origins": "*"}, r"/latest_alert": {"origins": "*"}})
logger.info("CORS enabled for all proctoring endpoints")

# =====================
# GLOBAL STATE (Thread-Safe)
# =====================
_state_lock = threading.Lock()
_exam_running = False
_suspicion_score = 0
_last_alert = ""

# Thread-safe getters and setters
def set_exam_running(value):
    global _exam_running
    with _state_lock:
        _exam_running = value
        logger.info(f"Exam running state set to: {value}")

def get_exam_running():
    with _state_lock:
        return _exam_running

def add_suspicion_score(value):
    global _suspicion_score
    with _state_lock:
        _suspicion_score += value
        logger.debug(f"Suspicion score increased by {value}, total: {_suspicion_score}")
        return _suspicion_score

def get_suspicion_score():
    with _state_lock:
        return _suspicion_score

def set_suspicion_score(value):
    global _suspicion_score
    with _state_lock:
        _suspicion_score = value
        logger.debug(f"Suspicion score set to: {value}")

def get_last_alert_message():
    with _state_lock:
        return _last_alert

def get_alert_payload():
    with _state_lock:
        return {
            "message": _last_alert,
            "score": _suspicion_score,
            "face_count": _detected_face_count,
            "head_movement": _detected_head_suspicious,
            "audio": _audio_suspicious,
            "time": time.strftime("%H:%M:%S")
        }

def set_last_alert(message):
    global _last_alert
    with _state_lock:
        _last_alert = message
        logger.info(f"Alert set: {message}")

# Legacy variable references (for backward compatibility)
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

_current_exam_user = None

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
# HOME PAGE - REDIRECT TO DETAILS
# =====================
@app.route("/")
def home():
    return render_template("details.html")

# =====================
# MAIN EXAM ENTRY (REDIRECTS TO WORKFLOW)
# =====================
@app.route("/exam")
def exam():
    """Entry point for exams.

    Always redirect to the verification workflow (personal details page)
    so that the user must go through:
      1) Personal Details
      2) Face Verification
      3) Start Exam (at /exam/start)
    """
    return redirect(url_for("home"))

# =====================
# USER DETAILS
# =====================
@app.route("/details")
def user_details():
    return render_template("details.html")

# =====================
# EXAM START PAGE (After workflow completion)
# =====================
@app.route("/exam/start")
def exam_start():
    """Start exam page.

    Only allow access if the user has completed:
      1) Personal details
      2) Face verification
    Otherwise redirect to the verification workflow.
    """
    # Simple token-based check: frontend passes ?verified=1 after successful verification
    verified = request.args.get('verified')
    if verified != '1':
        log_event(f"Unauthorized attempt to access /exam/start without verification token. Query params: {dict(request.args)}")
        return redirect(url_for("home"))
    log_event("Authorized access to /exam/start with verification token")
    return render_template("index.html")

@app.route("/exam/<path:filename>")
def exam_static(filename):
    """Serve static files from frontend directory for the exam page."""
    # Prevent serving index.html through static route
    if filename == 'index.html':
        return redirect(url_for("home"))
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'frontend'), filename)

@app.route("/submit_details", methods=["POST"])
def submit_details():
    # Handle both form data and JSON data
    if request.is_json:
        data = request.get_json()
        name = data.get("name")
        gender = data.get("gender")
        location = data.get("location")
    else:
        name = request.form.get("name")
        gender = request.form.get("gender")
        location = request.form.get("location")
    
    # Store user details in database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                location TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert user details
        cursor.execute('''
            INSERT INTO user_details (name, gender, location)
            VALUES (?, ?, ?)
        ''', (name, gender, location))
        
        conn.commit()
        conn.close()
        
        log_event(f"User details stored in database: {name}, {gender}, {location}")
        
    except Exception as e:
        log_event(f"Database error storing user details: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to store details"})
    
    return jsonify({"status": "success", "message": "Details submitted successfully"})

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
    """Pre-exam quick face verification endpoint.

    Uses the latest streaming frame when available, otherwise captures
    a fresh frame directly from the camera so verification does not fail
    with "No camera feed available" when /video_feed is not active.
    
    Also accepts base64 image data from frontend as fallback.
    """
    global _latest_frame

    # Check if frontend sent image data as fallback
    data = request.get_json(silent=True) or {}
    frontend_image = data.get('image_data')  # base64 encoded image
    
    if frontend_image:
        try:
            import base64
            # Decode base64 image
            image_data = base64.b64decode(frontend_image.split(',')[1]) if ',' in frontend_image else base64.b64decode(frontend_image)
            import numpy as np
            frame_array = np.frombuffer(image_data, dtype=np.uint8)
            frame_to_use = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame_to_use is None:
                return jsonify({
                    "status": "error",
                    "message": "Failed to decode image from frontend"
                })
            
            log_event("Using image data from frontend for verification")
        except Exception as e:
            log_event(f"Error processing frontend image: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Failed to process image from frontend: {str(e)}"
            })
    else:
        # Determine which frame to use for verification
        frame_to_use = None

        if _latest_frame is not None:
            # Use the most recent frame from the streaming worker
            frame_to_use = _latest_frame.copy()
            log_event("Using latest frame from video stream for verification")
        else:
            # Fallback: capture a single frame directly from the default camera
            log_event("No streaming frame available, attempting direct camera capture")
            try:
                # Try multiple camera indices with different backends
                camera_attempts = []
                
                # Try different camera backends and indices
                backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_V4L2, cv2.CAP_FFMPEG] if os.name == 'nt' else [cv2.CAP_V4L2, cv2.CAP_FFMPEG]
                
                for backend in backends:
                    for camera_index in [0, 1, 2]:
                        camera_attempts.append(f"Backend {backend}, Camera {camera_index}")
                        log_event(f"Trying backend {backend}, camera index {camera_index}")
                        
                        # Try with specific backend
                        cap = cv2.VideoCapture(camera_index + backend)
                        
                        if not cap.isOpened():
                            log_event(f"Camera {camera_index} with backend {backend} failed to open")
                            cap.release()
                            continue
                        
                        # Set camera settings for better capture
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        cap.set(cv2.CAP_PROP_FPS, 30)
                        cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
                        
                        # Allow camera to warm up
                        import time
                        time.sleep(2.0)  # Increased warm-up time
                        
                        # Try reading multiple frames with different settings
                        for attempt in range(8):  # More attempts
                            ret, frame = cap.read()
                            if ret and frame is not None:
                                # Check if frame is not completely black
                                if frame.mean() > 10:  # Frame has some content
                                    frame_to_use = frame
                                    log_event(f"Successfully captured valid frame from camera {camera_index} with backend {backend} (mean: {frame.mean():.1f})")
                                    cap.release()
                                    break
                                else:
                                    log_event(f"Frame {attempt} from camera {camera_index} appears dark (mean: {frame.mean():.1f})")
                            time.sleep(0.5)  # Longer wait between attempts
                            
                        cap.release()
                        if frame_to_use is not None:
                            break
                    
                    if frame_to_use is not None:
                        break
                
                if frame_to_use is None:
                    log_event(f"All camera attempts failed. Tried: {camera_attempts}")
                    return jsonify({
                        "status": "fallback_needed",
                        "message": "Backend camera access failed. Using frontend camera for verification..."
                    })
                    
            except Exception as e:
                log_event(f"Camera capture error during quick verification: {str(e)}")
                return jsonify({
                    "status": "fallback_needed",
                    "message": "Camera initialization failed. Using frontend camera for verification..."
                })

    # Check if frame is valid (not completely black)
    if frame_to_use is not None and frame_to_use.mean() < 10:
        log_event(f"Captured frame appears black (mean: {frame_to_use.mean():.1f}), forcing frontend fallback")
        return jsonify({
            "status": "fallback_needed",
            "message": "Backend camera captured dark frame. Using frontend camera as fallback."
        })

    # Read optional flags from request body
    store_snapshot = bool(data.get("store_snapshot", False))

    # Run quick verification on the selected frame
    verification_result = quick_face_verification(frame_to_use)

    # Handle different verification statuses
    if verification_result.get("verified"):
        # User is verified - means they already exist in the system
        # Save snapshot for verified user (even if already registered)
        snapshot_path = None
        try:
            snapshots_dir = os.path.join(os.path.dirname(__file__), "snapshots")
            os.makedirs(snapshots_dir, exist_ok=True)

            import time
            ts = int(time.time())
            safe_name = secure_filename(str(verification_result.get('name')))
            filename = f"{safe_name}_{ts}.jpg"
            snapshot_path = os.path.join(snapshots_dir, filename)

            ok = cv2.imwrite(snapshot_path, frame_to_use)
            if ok:
                conn = sqlite3.connect('proctoring.db')
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pre_exam_identity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        snapshot_path TEXT NOT NULL,
                        verified_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    INSERT INTO pre_exam_identity (name, snapshot_path)
                    VALUES (?, ?)
                ''', (verification_result.get('name'), snapshot_path))
                conn.commit()
                conn.close()
                log_event(f"Snapshot saved for verified user: {verification_result.get('name')}")
        except Exception as e:
            log_event(f"Failed to save snapshot: {str(e)}")

        return jsonify({
            "status": "warning",
            "message": f"User already exists: {verification_result.get('name', 'Unknown')}. Face already registered.",
            "verification": verification_result,
            "snapshot_path": snapshot_path
        })

    if verification_result.get("status") == "already_registered":
        return jsonify({
            "status": "warning",
            "message": "User already exists. Face already registered.",
            "verification": verification_result
        })

    if not verification_result.get("verified"):
        return jsonify({
            "status": "error",
            "message": verification_result.get("message", "Face verification failed. Please try again."),
            "verification": verification_result
        })

    # This should not be reached anymore, but keeping for safety
    return jsonify({
        "status": "error",
        "message": "Unexpected verification state",
        "verification": verification_result
    })

@app.route("/api/face_recognition/register", methods=["POST"])
def register_face_api():
    global _latest_frame
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        frontend_image = data.get('image_data')  # base64 encoded image
        
        if not name:
            return jsonify({
                "status": "error", 
                "message": "Name is required for registration"
            })

        # Choose a frame for registration: use latest worker frame if present,
        # otherwise capture a fresh frame from the default camera.
        frame_to_use = None

        if frontend_image:
            # Use frontend image if provided
            try:
                import base64
                # Decode base64 image
                image_data = base64.b64decode(frontend_image.split(',')[1]) if ',' in frontend_image else base64.b64decode(frontend_image)
                import numpy as np
                frame_array = np.frombuffer(image_data, dtype=np.uint8)
                frame_to_use = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                
                if frame_to_use is None:
                    return jsonify({
                        "status": "error",
                        "message": "Failed to decode image from frontend"
                    })
                
                log_event("Using image data from frontend for registration")
            except Exception as e:
                log_event(f"Error processing frontend image: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": f"Failed to process image from frontend: {str(e)}"
                })
        elif _latest_frame is not None:
            frame_to_use = _latest_frame.copy()
            log_event("Using latest frame from video stream for registration")
        else:
            log_event("No streaming frame available, attempting direct camera capture for registration")
            try:
                # Try multiple camera indices with better error handling
                for camera_index in [0, 1, 2]:
                    log_event(f"Trying camera index {camera_index} for registration")
                    cap = cv2.VideoCapture(camera_index)
                    
                    if not cap.isOpened():
                        log_event(f"Camera {camera_index} failed to open for registration")
                        continue
                    
                    # Set camera settings for better capture
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    
                    # Allow camera to warm up
                    import time
                    time.sleep(1.0)
                    
                    # Try multiple frame reads
                    for attempt in range(3):
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.mean() > 10:
                            frame_to_use = frame
                            log_event(f"Successfully captured valid frame from camera {camera_index} for registration")
                            break
                        time.sleep(0.2)
                    
                    cap.release()
                    if frame_to_use is not None:
                        break
                
                if frame_to_use is None:
                    return jsonify({
                        "status": "fallback_needed",
                        "message": "Backend camera access failed for registration. Please ensure camera permissions or the system will use frontend camera as fallback."
                    })
                    
            except Exception as e:
                error_msg = f"Camera error during registration: {str(e)}"
                log_event(error_msg)
                return jsonify({
                    "status": "fallback_needed",
                    "message": f"Camera initialization failed: {str(e)}. System will use frontend camera as fallback."
                })
        
        # Register the face from the selected frame
        result = register_new_user(frame_to_use, name)
        
        if result.get('status') == 'success':
            log_event(f"Face registered: {name}")
            # Save snapshot for successful registration
            try:
                snapshots_dir = os.path.join(os.path.dirname(__file__), "snapshots")
                os.makedirs(snapshots_dir, exist_ok=True)

                import time
                ts = int(time.time())
                safe_name = secure_filename(name)
                filename = f"{safe_name}_{ts}.jpg"
                snapshot_path = os.path.join(snapshots_dir, filename)

                ok = cv2.imwrite(snapshot_path, frame_to_use)
                if ok:
                    conn = sqlite3.connect('proctoring.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS pre_exam_identity (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            snapshot_path TEXT NOT NULL,
                            verified_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    cursor.execute('''
                        INSERT INTO pre_exam_identity (name, snapshot_path)
                        VALUES (?, ?)
                    ''', (name, snapshot_path))
                    conn.commit()
                    conn.close()
                    log_event(f"Snapshot saved for registered user: {name}")
            except Exception as e:
                log_event(f"Failed to save registration snapshot: {str(e)}")
        elif result.get('status') == 'already_registered':
            log_event(f"Attempt to re-register existing face: {name}")
            # Return warning status for already registered users
            return jsonify({
                "status": "warning",
                "message": f"User {name} already exists. Face already registered.",
                "details": result.get('message', f'User {name} is already registered.')
            })
        
        return jsonify(result)
            
    except Exception as e:
        error_msg = f"Registration error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({
            "status": "error", 
            "message": error_msg
        })

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

@app.route("/api/calibration/test", methods=["POST"])
def run_calibration_test_api():
    global _latest_frame
    try:
        current_status = get_calibration_status()
        
        if not current_status['is_running']:
            return jsonify({
                "status": "error",
                "message": "Calibration wizard not started"
            })
        
        current_step = current_status['current_step']
        test_type = current_status['test_type']
        
        if test_type is None:
            # For steps without tests (welcome, final_check)
            return jsonify({
                "status": "success",
                "message": "Step completed",
                "test_results": {"status": "completed", "message": "Setup step completed"}
            })
        
        # Run appropriate test
        if test_type == 'camera':
            results = run_calibration_test(_latest_frame, 'camera_position')
        elif test_type == 'face_verification':
            results = run_calibration_test(_latest_frame, 'face_verification')
        elif test_type == 'lighting':
            results = run_calibration_test(_latest_frame, 'lighting')
        elif test_type == 'face_detection':
            results = run_calibration_test(_latest_frame, 'face_detection')
        elif test_type == 'audio':
            results = run_calibration_test(None, 'audio')
        elif test_type == 'rules_confirmation':
            results = run_calibration_test(None, 'rules_confirmation')
        else:
            results = {"status": "error", "message": f"Unknown test type: {test_type}"}
        
        return jsonify({
            "status": "success",
            "test_results": results
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Calibration test failed: {str(e)}"
        })

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
    global _detected_face_count, _detected_head_suspicious

    event_cooldown_seconds = {
        "multiple_faces": 8.0,  # Increased from 3.0
        "head_movement": 5.0,    # Increased from 2.0
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
        try:
            if not get_exam_running():
                _detected_face_count = 0
                _detected_head_suspicious = False
                time.sleep(0.05)
                continue
        except Exception as e:
            logger.error(f"Error checking exam_running state in _detection_worker: {str(e)}", exc_info=True)
            time.sleep(0.1)
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
                        add_suspicion_score(2)
                        set_last_alert("Multiple faces detected")
                        generate_alert(get_last_alert_message())
                        log_event(get_last_alert_message())
            except Exception as e:
                logger.error(f"Face detection error in _detection_worker: {str(e)}", exc_info=True)

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
                        add_suspicion_score(1)
                        set_last_alert("Abnormal head movement")
                        generate_alert(get_last_alert_message())
                        log_event(get_last_alert_message())
            except Exception as e:
                logger.error(f"Head movement detection error in _detection_worker: {str(e)}", exc_info=True)

        frame_index += 1
        time.sleep(0.001)


def _audio_worker():
    global _audio_suspicious, _audio_last_check_time

    event_cooldown_seconds = 10.0  # Increased from 6.0

    audio_check_interval_seconds = 6.0

    while not _stop_event.is_set():
        if not get_exam_running():
            _audio_suspicious = False
            time.sleep(0.2)
            continue

        try:
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
                    add_suspicion_score(1)
                    set_last_alert("Background voice detected")
                    generate_alert(get_last_alert_message())
                    log_event(get_last_alert_message())
        except Exception as e:
            logger.error(f"Audio detection error in _audio_worker: {str(e)}", exc_info=True)


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
@app.route("/stop_camera", methods=["POST"])
def stop_camera():
    """Stop the camera feed and release resources"""
    global _camera, _latest_frame
    
    try:
        # Check if camera variable exists and is not None
        if '_camera' in globals() and _camera is not None:
            _camera.release()
            _camera = None
            _latest_frame = None
            logger.info("Camera stopped and resources released")
        else:
            logger.info("Camera was not running")
        
        return jsonify({"status": "success", "message": "Camera stopped"})
    except Exception as e:
        logger.error(f"Error stopping camera: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/start_exam", methods=["POST"])
def start_exam():
    global exam_running, suspicion_score, last_alert, _latest_frame, _current_exam_user

    # Since user was already verified in the details flow, we don't need strict verification here
    # Just check that we have a pre-exam verification record
    
    # Require a previously stored pre-exam identity 
    try:
        conn = sqlite3.connect('proctoring.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pre_exam_identity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                snapshot_path TEXT NOT NULL,
                verified_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            SELECT id, name, snapshot_path, verified_at
            FROM pre_exam_identity
            ORDER BY id DESC
            LIMIT 1
        ''')
        row = cursor.fetchone()
        conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": f"DB error: {str(e)}"}), 500

    if not row:
        return jsonify({"status": "error", "message": "No pre-exam verification found. Please verify face first."}), 400

    expected_name = row[1]
    
    # Only verify if we have a valid camera frame, otherwise skip verification
    # since user was already verified in the details flow
    if _latest_frame is not None:
        verification_result = quick_face_verification(_latest_frame)
        if verification_result.get('verified'):
            actual_name = verification_result.get('name')
            if expected_name and actual_name and expected_name != actual_name:
                return jsonify({
                    "status": "error",
                    "message": "User mismatch. The person starting the exam is not the same as the verified user.",
                    "expected": expected_name,
                    "actual": actual_name
                }), 403
        # If verification fails but user was already verified, allow it with a warning
        # This handles cases where camera lighting changed between verification and exam start
        else:
            log_event(f"Exam start verification failed for {expected_name}, but allowing since pre-exam verification exists")
    else:
        log_event(f"No camera frame available for exam start, but allowing {expected_name} since pre-exam verification exists")

    _current_exam_user = expected_name

    set_exam_running(True)
    set_suspicion_score(0)
    set_last_alert("")
    
    # Clear any existing alerts when starting exam
    clear_alert_queue()
    
    log_event("Exam started")
    return jsonify({"status": "success", "message": "Exam started"})


@app.route("/stop_exam")
def stop_exam():
    global _current_exam_user
    set_exam_running(False)
    _current_exam_user = None
    clear_alert_queue()
    return jsonify({"status": "stopped"})


# =====================
# TAB SWITCH (REAL – FROM JS)
# =====================
@app.route("/tab_switched", methods=["POST"])
def tab_switched():
    if not get_exam_running():
        return jsonify({"status": "ignored"})

    if detect_tab_switch():
        add_suspicion_score(1)
        set_last_alert("User switched browser tab")
        generate_alert(get_last_alert_message())
        log_event(get_last_alert_message())
        return jsonify({"status": "logged"})

    return jsonify({"status": "ignored"})


# =====================
# SCORE & ALERT APIs
# =====================
@app.route("/suspicion_score")
def get_score():
    return jsonify({"score": get_suspicion_score()})


@app.route("/latest_alert")
def get_alert():
    return jsonify(get_alert_payload())


# =====================
# RUN SERVER
# =====================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, threaded=True)
