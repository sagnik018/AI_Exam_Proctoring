// =====================
// START EXAM
// =====================
let examRunning = false;

function startExam() {
    fetch("http://127.0.0.1:5000/start_exam")
        .then(res => {
            if (res.ok) {
                examRunning = true;
                updateExamStatus("Exam Running", "green");
                showNotification("Exam started successfully", "success");
            } else {
                showNotification("Failed to start exam", "error");
            }
        })
        .catch(err => {
            showNotification("Backend not reachable", "error");
            console.error(err);
        });
}

// =====================
// STOP EXAM
// =====================
function stopExam() {
    // Check if exam is actually running
    if (!examRunning) {
        showNotification("Cannot stop exam - exam is not started yet!", "error");
        return;
    }
    
    fetch("http://127.0.0.1:5000/stop_exam")
        .then(() => {
            examRunning = false;
            updateExamStatus("Exam Stopped", "red");
            showNotification("Exam stopped", "info");
        })
        .catch(err => console.error(err));
}

// =====================
// UPDATE EXAM STATUS
// =====================
function updateExamStatus(text, color) {
    const statusEl = document.getElementById("examStatus");
    if (statusEl) {
        const colorClasses = {
            green: "bg-green-500",
            red: "bg-red-500",
            gray: "bg-gray-500"
        };
        
        statusEl.className = `${colorClasses[color] || colorClasses.gray} bg-opacity-80 rounded-lg px-4 py-2`;
        statusEl.querySelector("span").innerText = text;
    }
}

// =====================
// SHOW NOTIFICATIONS
// =====================
function showNotification(message, type = "info") {
    // Create notification element
    const notification = document.createElement("div");
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 alert-slide ${
        type === "success" ? "bg-green-500" : 
        type === "error" ? "bg-red-500" : 
        "bg-blue-500"
    } text-white font-semibold`;
    notification.innerText = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// =====================
// UPDATE SUSPICION SCORE
// =====================
setInterval(() => {
    fetch("http://127.0.0.1:5000/suspicion_score")
        .then(res => res.json())
        .then(data => {
            const scoreEl = document.getElementById("score");
            if (scoreEl) {
                const currentScore = parseInt(scoreEl.innerText);
                const newScore = data.score;
                
                // Add animation effect when score changes
                if (currentScore !== newScore) {
                    scoreEl.classList.add("pulse-animation");
                    setTimeout(() => {
                        scoreEl.classList.remove("pulse-animation");
                    }, 1000);
                }
                
                scoreEl.innerText = newScore;
                
                // Change color based on score level
                if (newScore >= 50) {
                    scoreEl.className = "text-2xl font-bold text-red-400";
                } else if (newScore >= 25) {
                    scoreEl.className = "text-2xl font-bold text-yellow-400";
                } else {
                    scoreEl.className = "text-2xl font-bold text-white";
                }
            }
        })
        .catch(err => console.error(err));
}, 2000);

// =====================
// SHOW ALERT MESSAGES
// =====================
setInterval(() => {
    fetch("http://127.0.0.1:5000/latest_alert")
        .then(res => res.json())
        .then(data => {
            const alertBox = document.getElementById("alertBox");
            const alertSection = document.getElementById("alertSection");
            const alertTime = document.getElementById("alertTime");
            
            if (!alertBox || !alertSection) return;

            const message = data.message || data.alert || "";
            const level = data.level || "";
            const time = data.time || "";

            if (!message) {
                alertSection.classList.add("hidden");
                return;
            }

            // Show alert section with animation
            alertSection.classList.remove("hidden");
            alertSection.classList.add("alert-slide");
            
            alertBox.innerText = message;
            if (alertTime) {
                alertTime.innerText = time;
            }
        })
        .catch(err => console.error(err));
}, 1500);

// =====================
// UPDATE TIMESTAMP
// =====================
function updateTimestamp() {
    const timestampEl = document.getElementById("timestamp");
    if (timestampEl) {
        const now = new Date();
        timestampEl.innerText = now.toLocaleTimeString();
    }
}

// Update timestamp every second
setInterval(updateTimestamp, 1000);
updateTimestamp(); // Initial call

// =====================
// REAL TAB SWITCH DETECTION
// =====================
document.addEventListener("visibilitychange", () => {
    if (document.hidden && examRunning) {
        fetch("http://127.0.0.1:5000/tab_switched", {
            method: "POST"
        }).catch(err => console.error(err));

        showNotification("Warning: Tab switching detected!", "error");
    }
});
