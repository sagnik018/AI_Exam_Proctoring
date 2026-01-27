# AI-Based Online Exam Proctoring System

A comprehensive AI-assisted proctoring system for online exams featuring advanced monitoring capabilities, real-time alerts, and a modern user interface.

## 🎯 Core Features

### **Proctoring & Monitoring**
- **Live Webcam Monitoring** - Real-time face detection and tracking
- **Head Movement Analysis** - MediaPipe-based head pose monitoring
- **Background Audio Detection** - Voice activity monitoring
- **Tab Switching Detection** - Browser visibility change tracking
- **Screen Recording** - Periodic screenshots for evidence collection
- **Face Recognition** - User authentication before exam start

### **User Interface**
- **Modern Glass Morphism Design** - Beautiful blur effects and transparency
- **Dynamic Theme System** - Light, Dark, Blue, and Purple themes
- **Responsive Design** - Works seamlessly on mobile and desktop
- **Real-time Status Updates** - Live alerts and monitoring indicators
- **Interactive Warning System** - Dynamic warning displays replacing start buttons

### **Alert & Security**
- **Color-coded Severity Levels** - Red (Critical), Orange (Warning), Blue (Info)
- **Automatic Escalation** - Progressive violation tracking
- **Suspicion Score System** - Real-time risk assessment
- **Comprehensive Logging** - SQLite database for all events
- **Admin Dashboard** - Statistics and detailed event logs

---

## 🚀 New Features Implemented

### **1. Enhanced User Verification Flow**
- **Multi-step Registration Process** - User details → Face verification → Exam access
- **Real-time Face Recognition** - Quick verification before exam start
- **Registration Fallback** - Automatic user registration if not found
- **Theme-aware UI** - Proper text colors in light/dark themes

### **2. Dynamic Warning System**
- **Live Warning Overlays** - Replaces start buttons with real-time alerts
- **Multiple Alert Types**:
  - ⚠️ Face Not Detected
  - 🚨 Abnormal Movement Detected
  - 👥 Multiple Faces Detected
  - 👀 Looking Away from Screen
  - 🔊 Background Noise Detected
  - 🔄 Tab Switching Detected
- **Auto-dismiss Warnings** - 5-second display with button restoration

### **3. Advanced Monitoring Features**
- **Screen Recording** - Automatic screenshots every 60 seconds
- **Enhanced Face Detection** - Multiple face recognition states
- **Movement Tracking** - Real-time abnormal movement alerts
- **Audio Monitoring** - Background voice detection with sensitivity control

### **4. Theme & UI Improvements**
- **4 Built-in Themes** - Light, Dark, Blue, Purple
- **System Theme Detection** - Automatic theme preference
- **Dark Mode Optimization** - White text on dark backgrounds
- **Responsive Grid Layout** - 6-column feature grid

### **5. Camera & Resource Management**
- **Automatic Webcam Shutdown** - Camera turns off on exam exit
- **Resource Cleanup** - Proper memory and hardware release
- **Error Handling** - Graceful camera failure recovery

---

## 📁 Project Structure

```
AI_Exam_Proctoring/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── proctoring/
│   │   ├── face_detection.py
│   │   ├── eye_head_detection.py
│   │   ├── audio_detection.py
│   │   ├── screen_monitor.py
│   │   └── face_recognition.py
│   └── database/
│       └── db.py              # SQLite logging
├── frontend/
│   ├── index.html             # Main exam interface
│   ├── details.html           # User registration/verification
│   ├── admin.html             # Admin dashboard
│   ├── exam.js                # Core exam functionality
│   ├── enhanced_features.js   # Advanced features
│   └── themes.css             # Theme system
└── screenshots/               # Screen capture storage
```

---

## 🛠️ Installation & Setup

### **Prerequisites**
- Windows 10/11 (optimized for Windows)
- Python 3.9+
- Working webcam and microphone
- Modern web browser

### **1. Clone & Setup Environment**
```bash
git clone <repository-url>
cd AI_Exam_Proctoring
python -m venv venv
venv\Scripts\activate  # Windows
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Start the Application**
```bash
cd backend
python app.py
```

**Access the application at:** `http://127.0.0.1:5000/`

---

## 📖 User Guide

### **Exam Flow**
1. **User Registration** - Enter name, gender, location
2. **Face Verification** - Camera scans and registers face
3. **Exam Start** - Begin monitoring with real-time alerts
4. **Live Monitoring** - Continuous proctoring with warnings
5. **Exam Exit** - Automatic camera shutdown and cleanup

### **Admin Dashboard**
- **URL:** `http://127.0.0.1:5000/admin/logs`
- **Features:** Event statistics, detailed logs, severity tracking
- **Real-time Updates:** Live monitoring of exam sessions

### **Theme Switching**
- **Location:** Top-right theme toggle button
- **Options:** Light, Dark, Blue, Purple
- **Auto-detection:** System preference detection

---

## 🔧 API Endpoints

### **Core Exam Operations**
- `GET /` - Main exam interface
- `GET /details` - User registration page
- `POST /start_exam` - Start exam session
- `POST /stop_exam` - Stop exam session
- `POST /stop_camera` - Shutdown webcam

### **Monitoring & Detection**
- `GET /video_feed` - MJPEG webcam stream
- `POST /submit_details` - Submit user registration
- `POST /verify_face` - Face verification
- `POST /register_face` - Face registration

### **Enhanced Features**
- `POST /start_screen_recording` - Begin screen capture
- `POST /stop_screen_recording` - Stop screen capture
- `GET /screen_recording_status` - Recording status
- `GET /calibration_results` - Calibration data
- `POST /tab_switched` - Log tab switching

### **Alerts & Statistics**
- `GET /suspicion_score` - Current suspicion score
- `GET /latest_alert` - Most recent alert
- `GET /alert_statistics` - Alert statistics
- `GET /admin/logs` - Admin dashboard data

---

## 🎨 UI Features

### **Glass Morphism Design**
- **Blur Effects** - Modern translucent panels
- **Gradient Backgrounds** - Purple to blue gradients
- **Smooth Animations** - Hover states and transitions
- **Professional Layout** - Clean, organized interface

### **Interactive Elements**
- **Dynamic Warning Display** - Replaces buttons with alerts
- **Real-time Status Updates** - Live monitoring indicators
- **Toast Notifications** - Non-intrusive alert system
- **Responsive Grid** - Mobile-friendly layout

### **Theme System**
- **Light Theme** - Clean, bright interface
- **Dark Theme** - Easy on the eyes for long sessions
- **Blue/Purple Themes** - Custom color schemes
- **System Detection** - Automatic theme preference

---

## 🚨 Alert System

### **Alert Types & Severity**
1. **Critical (Red)** - Multiple faces, unauthorized person
2. **Warning (Orange)** - No face detected, abnormal movement
3. **Info (Blue)** - System notifications, status updates

### **Escalation Rules**
- **3 Violations** → Automatic escalation
- **Score Tracking** - Progressive suspicion scoring
- **Auto-dismiss** - 5-second warning display

### **Monitoring Features**
- **Face Detection** - Real-time face tracking
- **Movement Analysis** - Head pose and movement monitoring
- **Audio Detection** - Background voice monitoring
- **Tab Detection** - Browser navigation tracking

---

## 🔒 Security Features

### **User Authentication**
- **Face Recognition** - Pre-exam user verification
- **Registration System** - Secure user enrollment
- **Session Management** - Controlled exam sessions

### **Monitoring & Evidence**
- **Screen Recording** - Periodic screenshots
- **Event Logging** - Comprehensive activity tracking
- **Real-time Alerts** - Immediate violation detection

### **Resource Management**
- **Automatic Cleanup** - Camera and resource release
- **Error Recovery** - Graceful failure handling
- **Memory Management** - Optimized resource usage

---

## 🛠️ Troubleshooting

### **Camera Issues**
- **Blank Video** - Close other camera applications
- **Permissions** - Check Windows camera permissions
- **Multiple Cameras** - Adjust camera index in `app.py`

### **Audio Problems**
- **PyAudio Installation** - Use prebuilt wheels for Windows
- **Sensitivity** - Adjust microphone gain in Windows settings
- **Background Noise** - Increase detection thresholds

### **Performance Issues**
- **High CPU Usage** - Reduce detection frequency
- **Memory Usage** - Restart application periodically
- **Network Issues** - Check localhost connectivity

---

## 📊 Tech Stack

### **Backend**
- **Python 3.9+** - Core programming language
- **Flask** - Web framework and API server
- **OpenCV** - Computer vision and image processing
- **MediaPipe** - Face detection and pose estimation
- **SQLite** - Database for logging and user data

### **Frontend**
- **HTML5/CSS3** - Modern web standards
- **Tailwind CSS** - Utility-first CSS framework
- **JavaScript (ES6+)** - Interactive functionality
- **SVG Icons** - Scalable vector graphics

### **Libraries & Dependencies**
- **SpeechRecognition** - Voice activity detection
- **PyAudio** - Audio input handling
- **Pillow** - Image processing and screenshots
- **Threading** - Concurrent processing

---

## 🎯 Performance Notes

### **Optimized Pipeline**
- **Threaded Architecture** - Separate capture and detection threads
- **Frame Rate Management** - Balanced FPS for smooth streaming
- **Memory Efficiency** - Optimized resource usage
- **Scalable Design** - Handles multiple concurrent users

### **Detection Accuracy**
- **Face Recognition** - High accuracy user verification
- **Movement Tracking** - Sensitive head pose detection
- **Audio Monitoring** - Adjustable sensitivity levels
- **Tab Detection** - Reliable browser monitoring

---

## 🔄 Future Enhancements

### **Planned Features**
- **Multi-camera Support** - Multiple angle monitoring
- **AI-powered Analysis** - Machine learning for behavior patterns
- **Cloud Integration** - Remote storage and processing
- **Mobile App** - Native mobile monitoring application

### **Improvements**
- **Better Face Recognition** - Enhanced accuracy and speed
- **Advanced Analytics** - Detailed behavior analysis
- **Customizable Rules** - Flexible violation detection
- **Integration APIs** - Third-party system integration

---

## 📝 License & Credits

This project demonstrates advanced AI proctoring capabilities with modern web technologies. Features include real-time monitoring, intelligent alert systems, and a professional user interface.

**Key Achievements:**
- ✅ Complete AI proctoring system
- ✅ Modern responsive UI with themes
- ✅ Real-time monitoring and alerts
- ✅ Face recognition authentication
- ✅ Screen recording and evidence collection
- ✅ Comprehensive admin dashboard
- ✅ Automatic resource management

---

**Ready for production use with enterprise-grade monitoring capabilities!** 🚀