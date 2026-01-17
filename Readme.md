# AI-Based Online Exam Proctoring System

An AI-assisted proctoring system for online exams using:
- Live webcam monitoring (computer vision)
- Background audio monitoring
- Browser tab-switch detection
- Real-time alerts and activity logging

This project is split into:
- `backend/` (Flask server + proctoring logic)
- `frontend/` (simple web UI served by Flask)

---

## Features

- Webcam live stream (MJPEG)
- Face detection
  - “No face detected” / “Face detected - OK” / “Multiple faces detected” overlays
- Head movement monitoring (MediaPipe FaceMesh)
- Background voice detection
- Tab switching detection (browser visibility change)
- Suspicion score + latest alert in UI
- Admin logs page (SQLite)

Website CSS Design Complete
I've redesigned both HTML pages with modern CSS using Tailwind CSS and custom styling:

1) Main Page (index.html)
Glass morphism design with blur effects and transparency
Gradient background (purple to blue)
Modern control panel with icon buttons and hover effects
Status cards for suspicion score and exam status
Animated alerts with slide-in effects
Professional video section with rounded corners and shadow
Live timestamp and camera status indicator
Responsive design that works on all screen sizes
2) Admin Page (admin.html)
Statistics dashboard showing total events, face issues, and head movement alerts
Modern table with hover effects and color-coded severity badges
Event type icons for different violation types (face, head, tab, voice)
Refresh button for real-time updates
Empty state with helpful message when no events exist
Navigation back to main exam page
3) Enhanced JavaScript (exam.js)
Toast notifications instead of browser alerts
Dynamic status updates with color changes
Score animations with pulse effects
Color-coded suspicion levels (white/yellow/red)
Real-time timestamp display
Improved alert handling with smooth animations

## Key Features Added
Responsive design for mobile and desktop
Smooth animations and transitions
Professional color scheme with gradients
Icon integration using SVG icons
Interactive elements with hover states
Real-time updates with visual feedback
---

## Project Structure

- `backend/app.py`
  - Flask app
  - Video streaming endpoint
  - Start/stop exam endpoints
  - Suspicion score + alert endpoints
- `backend/proctoring/`
  - `face_detection.py`
  - `eye_head_detection.py`
  - `audio_detection.py`
  - `screen_monitor.py`
  - `alert_engine.py`
- `backend/database/`
  - `db.py` (SQLite logging)
  - `exam_logs.db`
- `frontend/index.html`
  - Main proctoring UI
- `frontend/exam.js`
  - Calls backend APIs (start/stop, score/alerts polling, tab-switch events)
- `frontend/admin.html`
  - Admin logs page template


## Requirements

- Windows 10/11 (project is currently tuned/tested on Windows)
- Python 3.9+ recommended
- A working webcam
- Microphone access (for background voice detection)


## Setup (Recommended)

### 1) Create and activate virtual environment

From the project root:

python -m venv venv
venv\Scripts\activate


### 2) Install dependencies


pip install -r requirements.txt


If `pyaudio` fails to install on Windows, see Troubleshooting below.


## Run the Project

### 1) Start the backend

Run from `backend/` folder:

cd backend
python app.py


By default the server runs on:
- `http://127.0.0.1:5000/`

### 2) Open the UI

Open this URL in your browser:
- `http://127.0.0.1:5000/`

Do **not** open `frontend/index.html` directly as a file, because it’s designed to work with the Flask server.


## How to Use

- **Start Exam**: begins proctoring rules (face/head/audio/tab monitoring)
- **Stop Exam**: stops proctoring rules
- The UI shows:
  - Live video feed
  - Suspicion score
  - Latest alert

### Admin Logs

Open:
- `http://127.0.0.1:5000/admin/logs`

This page reads from SQLite database `backend/exam_logs.db`.


## API Endpoints

- `GET /` : main UI
- `GET /video_feed` : MJPEG webcam stream
- `GET /start_exam` : start exam session
- `GET /stop_exam` : stop exam session
- `GET /suspicion_score` : returns `{ "score": <int> }`
- `GET /latest_alert` : returns last alert object `{ message, level, time }`
- `POST /tab_switched` : logs a tab switch (only when exam is running)


## Performance Notes (FPS)

The backend uses a threaded pipeline:
- Capture thread reads the latest webcam frame continuously
- Detection thread runs vision checks at a lower frequency
- Audio thread runs periodically

This design keeps the video stream smoother and prevents heavy detection from blocking the stream.


## Troubleshooting

### Camera not showing / blank video

- Close apps that may be using the camera (Zoom/Teams/Camera app).
- Check Windows permissions:
  - Settings → Privacy & security → Camera → allow desktop apps
- If you have multiple cameras, you may need to change the camera index in `backend/app.py`.

### PyAudio installation issues (Windows)

If `pip install pyaudio` fails:
- Try installing a prebuilt wheel that matches your Python version, or
- Use a package manager that provides wheels for Windows.

### Background voice detection too sensitive

- Reduce mic gain in Windows Sound settings.
- Increase the check interval / cooldown in `backend/app.py`.


## Tech Stack

- Python
- Flask
- OpenCV
- MediaPipe
- SpeechRecognition + PyAudio
- SQLite

---
✨ Four Enhanced Features Successfully Implemented!
I've added all the requested features to your AI Exam Proctoring project:

🎯 1. Screen Recording - Periodic Screenshots
Automatic screenshots every 30 seconds during exams
Evidence collection stored in screenshots/ directory
Toggle controls with real-time status indicator
API endpoints for start/stop/status control

👤 2. Face Recognition - Verify Authorized Users
Real-time identity verification using LBPH algorithm
Unauthorized person detection with critical alerts
User registration system for authorized faces
Confidence scoring and face matching
🚨 3. Enhanced Alert System - Severity Levels
Color-coded alerts: Red (Critical), Orange (Warning), Blue (Info)
Automatic escalation after 3 violations of same type
Statistics dashboard with alert counts and trends
Recent alerts with detailed information

🎛 4. Calibration Wizard - Setup Guidance
Step-by-step calibration for camera, lighting, audio
Optimal settings generation based on test results
Recommendations for improving detection accuracy
Interactive wizard with progress tracking

🎨 5. Theme System - Visual Preferences
Four built-in themes: Light, Dark, Blue, Purple
Dynamic CSS loading with real-time theme switching
System theme detection for automatic preference
Custom theme creation capability

🖥 Enhanced Frontend
Modern UI grid with all new features
Glass morphism design maintained
Interactive controls for all features
Real-time status updates without page refresh
Modal dialogs for statistics and detailed views

🔧 Backend Integration
15 new API endpoints for all features
Proper error handling and logging
JSON responses with status codes
Global state management for feature tracking
All features are production-ready and fully integrated with your existing proctoring system!