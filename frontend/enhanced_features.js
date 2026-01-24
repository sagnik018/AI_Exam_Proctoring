// =====================
// ENHANCED FEATURES JAVASCRIPT
// =====================

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

// Show Exam Rules Modal
function showExamRules() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-3xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-3xl font-bold text-gray-800">📋 Exam Rules to Follow</h2>
                <button onclick="closeRulesModal()" class="text-gray-500 hover:text-gray-700">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            
            <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
                <h3 class="font-bold text-red-800 mb-2">⚠️ IMPORTANT: Complete All Verification Steps</h3>
                <p class="text-red-700">You must complete all verification steps before starting the exam. Follow all rules to ensure fair examination.</p>
            </div>
            
            <!-- Verification Requirements -->
            <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
                <h3 class="font-bold text-blue-800 mb-3">✅ Required Verifications</h3>
                <ul class="space-y-2 text-blue-700">
                    <li class="flex items-start">
                        <span class="text-blue-500 mr-2">✓</span>
                        <span><strong>Personal Details:</strong> Provide your full name, gender, and location</span>
                    </li>
                    <li class="flex items-start">
                        <span class="text-blue-500 mr-2">✓</span>
                        <span><strong>Face Verification:</strong> Verify your identity using facial recognition</span>
                    </li>
                    <li class="flex items-start">
                        <span class="text-blue-500 mr-2">✓</span>
                        <span><strong>Exam Rules:</strong> Read and accept all examination rules</span>
                    </li>
                </ul>
                    
                <div class="bg-green-50 p-4 rounded-lg mt-4">
                    <h4 class="font-semibold text-green-800 mb-2">🎯 Examination Protocol</h4>
                    <ul class="space-y-2 text-green-700">
                        <li class="flex items-start">
                            <span class="text-green-500 mr-2">•</span>
                            <span>Follow all examiner instructions</span>
                        </li>
                        <li class="flex items-start">
                            <span class="text-green-500 mr-2">•</span>
                            <span>Stay within camera frame at all times</span>
                        </li>
                        <li class="flex items-start">
                            <span class="text-green-500 mr-2">•</span>
                            <span>Ensure good lighting and visibility</span>
                        </li>
                        <li class="flex items-start">
                            <span class="text-green-500 mr-2">•</span>
                            <span>Report technical issues immediately</span>
                        </li>
                    </ul>
                </div>
            </div>
            
            <div class="bg-gray-100 p-4 rounded-lg mb-6">
                <h4 class="font-semibold text-gray-800 mb-2">🔍 Monitoring & Detection</h4>
                <p class="text-gray-700 mb-2">The system will monitor and detect:</p>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    <div class="bg-white p-2 rounded text-center">👥 Multiple Faces</div>
                    <div class="bg-white p-2 rounded text-center">👀 Head Movement</div>
                    <div class="bg-white p-2 rounded text-center">🗣️ Background Voice</div>
                    <div class="bg-white p-2 rounded text-center">🔄 Tab Switching</div>
                </div>
            </div>
            
            <div class="flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <input type="checkbox" id="rulesAccepted" class="w-4 h-4 text-blue-600">
                    <label for="rulesAccepted" class="text-gray-800 font-medium">
                        I have read and understood all exam rules
                    </label>
                </div>
                <div class="space-x-2">
                    <button onclick="closeRulesModal()" class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded">
                        Cancel
                    </button>
                    <button onclick="acceptRules()" class="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded" disabled id="acceptRulesBtn">
                        I Accept - Start Exam
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Enable accept button only when checkbox is checked
    const checkbox = document.getElementById('rulesAccepted');
    const acceptBtn = document.getElementById('acceptRulesBtn');
    
    checkbox.addEventListener('change', function() {
        acceptBtn.disabled = !this.checked;
    });
}

function acceptRules() {
    const checkbox = document.getElementById('rulesAccepted');
    if (!checkbox.checked) {
        showNotification("Please accept the exam rules first", "error");
        return;
    }
    
    closeRulesModal();
    showNotification("Rules accepted! You can now start the exam.", "success");
}

function closeRulesModal() {
    const modal = document.querySelector('.fixed.inset-0');
    if (modal) modal.remove();
}

// Calibration Wizard Functions
let calibrationStep = 0;
let calibrationData = {};

function startCalibrationWizard() {
    showNotification("Starting calibration wizard...", "info");
    
    fetch("/api/calibration/start", {
        method: "POST"
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            calibrationStep = 0;
            showCalibrationStep();
        }
    })
    .catch(err => {
        console.error(err);
        showNotification("Failed to start calibration", "error");
    });
}

function showCalibrationStep() {
    fetch("/api/calibration/status")
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            const calibration = data.calibration;
            showCalibrationModal(calibration);
        }
    })
    .catch(err => console.error(err));
}

function showCalibrationModal(calibration) {
    // Create modal for calibration step
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-2xl font-bold text-gray-800">${calibration.title}</h2>
                <button onclick="closeCalibrationModal()" class="text-gray-500 hover:text-gray-700">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            
            <div class="mb-4">
                <p class="text-gray-600 mb-4">${calibration.description}</p>
                
                <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
                    <h3 class="font-semibold text-blue-800 mb-2">Instructions:</h3>
                    <ul class="list-disc list-inside text-blue-700 space-y-1">
                        ${calibration.instructions.map(instruction => `<li>${instruction}</li>`).join('')}
                    </ul>
                </div>
                
                ${calibration.test_type ? `
                    <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 mb-4">
                        <p class="text-yellow-700">Click "Test This Step" to run the calibration test.</p>
                    </div>
                ` : ''}
            </div>
            
            <div class="flex justify-between">
                <button onclick="closeCalibrationModal()" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded">
                    Cancel
                </button>
                <div class="space-x-2">
                    ${calibration.test_type ? `
                        <button onclick="testCalibrationStep()" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
                            Test This Step
                        </button>
                    ` : ''}
                    <button onclick="nextCalibrationStep()" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">
                        ${calibration.test_type ? 'Skip Test' : 'Next Step'}
                    </button>
                </div>
            </div>
            
            <div class="mt-4">
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-blue-600 h-2 rounded-full" style="width: ${calibration.progress || 0}%"></div>
                </div>
                <p class="text-sm text-gray-600 mt-1">Step ${calibration.current_step_index + 1} of ${calibration.total_steps}</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function testCalibrationStep() {
    showNotification("Running calibration test...", "info");
    
    fetch("/api/calibration/test", {
        method: "POST"
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            const results = data.test_results;
            showCalibrationResults(results);
        } else {
            showNotification("Calibration test failed", "error");
        }
    })
    .catch(err => {
        console.error(err);
        showNotification("Calibration test error", "error");
    });
}

function showCalibrationResults(results) {
    const resultsModal = document.createElement('div');
    resultsModal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    
    let recommendations = '';
    if (results.recommendations && results.recommendations.length > 0) {
        recommendations = `
            <div class="mt-4">
                <h4 class="font-semibold text-gray-800 mb-2">Recommendations:</h4>
                <ul class="list-disc list-inside text-gray-700 space-y-1">
                    ${results.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    resultsModal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
            <h3 class="text-xl font-bold text-gray-800 mb-4">Calibration Test Results</h3>
            
            <div class="mb-4">
                <p class="text-gray-600">${results.message || 'Test completed'}</p>
                ${results.verified ? '<p class="text-green-600 font-semibold">✅ Verification Successful</p>' : ''}
                ${results.status === 'error' ? '<p class="text-red-600 font-semibold">❌ Test Failed</p>' : ''}
            </div>
            
            ${recommendations}
            
            <div class="flex justify-end">
                <button onclick="closeCalibrationResults()" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
                    Close
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(resultsModal);
}

function closeCalibrationResults() {
    const modal = document.querySelector('.fixed.inset-0');
    if (modal) modal.remove();
}

function nextCalibrationStep() {
    fetch("/api/calibration/next", {
        method: "POST"
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            const result = data.result;
            if (result.status === 'completed') {
                showNotification("Calibration completed successfully!", "success");
                closeCalibrationModal();
            } else {
                showCalibrationStep();
            }
        }
    })
    .catch(err => {
        console.error(err);
        showNotification("Failed to proceed to next step", "error");
    });
}

function closeCalibrationModal() {
    const modal = document.querySelector('.fixed.inset-0');
    if (modal) modal.remove();
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
            // Force CSS refresh by adding timestamp
            const themeLink = document.getElementById("theme-css");
            if (themeLink) {
                themeLink.href = `/themes.css?t=${Date.now()}`;
            }
            showNotification(`Theme changed to ${selectedTheme}`, "success");
        }
    })
    .catch(err => {
        console.error(err);
        showNotification("Failed to change theme", "error");
    });
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
