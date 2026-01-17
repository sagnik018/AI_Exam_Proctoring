// =====================
// ENHANCED FEATURES JAVASCRIPT
// =====================

// Face Verification Before Exam
function verifyFaceBeforeExam() {
    return new Promise((resolve, reject) => {
        showNotification("Verifying face identity...", "info");
        
        fetch("/api/face_recognition/verify_quick", {
            method: "POST"
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                const verification = data.verification;
                
                if (verification.verified) {
                    showNotification(verification.message, "success");
                    resolve(true);
                } else {
                    showNotification(verification.message, "error");
                    resolve(false);
                }
            } else {
                showNotification("Face verification failed", "error");
                resolve(false);
            }
        })
        .catch(err => {
            console.error(err);
            showNotification("Face verification error", "error");
            resolve(false);
        });
    });
}

// Face Registration
function registerFace() {
    const name = prompt("Enter your name for face registration:");
    if (!name) return;
    
    showNotification("Capturing face for registration...", "info");
    
    // Capture current frame and register
    fetch("/api/face_recognition/register", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: name })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            showNotification(`Face registered successfully! ${name}, you can now start the exam.`, "success");
            showNotification("✅ Verified permission given to start the test!", "success");
        } else if (data.status === "info") {
            showNotification(data.message, "info");
        } else {
            showNotification("Face registration failed", "error");
        }
    })
    .catch(err => {
        console.error(err);
        showNotification("Face registration error", "error");
    });
}

// Enhanced Start Exam with Face Verification
async function startExamWithVerification() {
    const verified = await verifyFaceBeforeExam();
    
    if (verified) {
        // Call original startExam function
        startExam();
    } else {
        showNotification("Face verification failed. Exam not started.", "error");
    }
}

// Screen Recording Functions
function toggleScreenRecording() {
    fetch("/api/screen_recording/toggle", {
        method: "POST"
    })
    .then(res => res.json())
    .then(data => {
        updateScreenRecordingStatus(data.recording);
        if (data.recording) {
            showNotification("Screen recording started", "info");
        } else {
            showNotification("Screen recording stopped", "info");
        }
    })
    .catch(err => console.error(err));
}

function updateScreenRecordingStatus(isRecording) {
    const statusEl = document.getElementById("screenRecordingStatus");
    if (statusEl) {
        statusEl.innerText = isRecording ? "Active" : "Inactive";
        statusEl.className = isRecording ? "text-green-400 text-xs" : "text-gray-300 text-xs";
    }
}

// Calibration Functions
function startCalibration() {
    fetch("/api/calibration/start", {
        method: "POST"
    })
    .then(res => res.json())
    .then(data => {
        updateCalibrationStatus(data.calibration);
        showNotification("Calibration wizard started", "info");
    })
    .catch(err => console.error(err));
}

function updateCalibrationStatus(calibration) {
    const statusEl = document.getElementById("calibrationStatus");
    if (statusEl && calibration.status) {
        statusEl.innerText = calibration.current_step || "Not Started";
        statusEl.className = "text-gray-300 text-xs";
    }
}

// Theme Functions
function changeTheme() {
    const selector = document.getElementById("themeSelector");
    const selectedTheme = selector.value;
    
    fetch(`/api/themes/set/${selectedTheme}`, {
        method: "POST"
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            updateThemeCSS(data.current_theme);
            showNotification(`Theme changed to ${selectedTheme}`, "success");
        }
    })
    .catch(err => console.error(err));
}

function updateThemeCSS(themeName) {
    // Update the theme CSS link
    const themeLink = document.getElementById("theme-css");
    if (themeLink) {
        themeLink.href = `/themes.css?t=${Date.now()}`;
    }
}

// Alert Statistics Functions
function showAlertStats() {
    fetch("/api/alerts/statistics")
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            displayAlertStatistics(data.statistics);
        }
    })
    .catch(err => console.error(err));
}

function displayAlertStatistics(stats) {
    // Create modal or update existing one
    let modal = document.getElementById("statsModal");
    if (!modal) {
        modal = createStatsModal();
        document.body.appendChild(modal);
    }
    
    // Update modal content
    const content = modal.querySelector("#statsContent");
    if (content) {
        content.innerHTML = `
            <div class="mb-4">
                <h3 class="text-lg font-bold mb-2">Alert Statistics</h3>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <p class="text-sm text-gray-600">Total Alerts</p>
                        <p class="text-2xl font-bold">${stats.total_alerts}</p>
                    </div>
                    <div>
                        <p class="text-sm text-gray-600">Critical Alerts</p>
                        <p class="text-2xl font-bold text-red-500">${stats.by_severity.critical}</p>
                    </div>
                    <div>
                        <p class="text-sm text-gray-600">Warning Alerts</p>
                        <p class="text-2xl font-bold text-yellow-500">${stats.by_severity.warning}</p>
                    </div>
                    <div>
                        <p class="text-sm text-gray-600">Info Alerts</p>
                        <p class="text-2xl font-bold text-blue-500">${stats.by_severity.info}</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    modal.classList.remove("hidden");
}

function createStatsModal() {
    const modal = document.createElement("div");
    modal.id = "statsModal";
    modal.className = "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden";
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-2xl mx-4">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl font-bold">Alert Statistics</h2>
                <button onclick="closeStatsModal()" class="text-gray-500 hover:text-gray-700">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            <div id="statsContent">
                <!-- Content will be populated by displayAlertStatistics -->
            </div>
        </div>
    `;
    return modal;
}

function closeStatsModal() {
    const modal = document.getElementById("statsModal");
    if (modal) {
        modal.classList.add("hidden");
    }
}

// Enhanced Alert Functions
function updateEnhancedAlerts() {
    fetch("/api/alerts/recent?count=5")
    .then(res => res.json())
    .then(data => {
        if (data.status === "success" && data.alerts.length > 0) {
            const latestAlert = data.alerts[0];
            updateEnhancedAlertSection(latestAlert);
        }
    })
    .catch(err => console.error(err));
}

function updateEnhancedAlertSection(alert) {
    const alertBox = document.getElementById("enhancedAlertBox");
    const severityEl = document.getElementById("enhancedAlertSeverity");
    const timeEl = document.getElementById("enhancedAlertTime");
    const section = document.getElementById("enhancedAlertSection");
    
    if (alertBox && severityEl && timeEl) {
        alertBox.innerText = alert.message;
        severityEl.innerText = alert.severity.toUpperCase();
        severityEl.className = getSeverityColorClass(alert.severity);
        timeEl.innerText = new Date(alert.timestamp * 1000).toLocaleTimeString();
        
        section.classList.remove("hidden");
        section.classList.add("alert-slide");
    }
}

function getSeverityColorClass(severity) {
    const colorClasses = {
        'critical': 'text-red-400',
        'warning': 'text-yellow-400',
        'info': 'text-blue-400'
    };
    return colorClasses[severity] || 'text-gray-400';
}

function dismissAlert() {
    const section = document.getElementById("enhancedAlertSection");
    if (section) {
        section.classList.add("hidden");
    }
}

function escalateAlert() {
    // This would typically escalate to admin or send notifications
    showNotification("Alert escalated to administrator", "error");
    dismissAlert();
}

// Auto-update enhanced alerts every 3 seconds
setInterval(updateEnhancedAlerts, 3000);

// Initialize enhanced features on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load current theme
    fetch("/api/themes")
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                const selector = document.getElementById("themeSelector");
                if (selector) {
                    selector.value = data.current_theme;
                }
            }
        })
        .catch(err => console.error(err));
    
    // Load screen recording status
    fetch("/api/screen_recording/status")
        .then(res => res.json())
        .then(data => {
            updateScreenRecordingStatus(data.recording);
        })
        .catch(err => console.error(err));
});
