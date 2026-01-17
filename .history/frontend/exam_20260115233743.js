// =====================
// START EXAM
// =====================
function startExam() {
    fetch("http://127.0.0.1:5000/start_exam")
        .then(res => {
            if (res.ok) {
                alert("Exam started");
            } else {
                alert("Failed to start exam");
            }
        })
        .catch(err => {
            alert("Backend not reachable");
            console.error(err);
        });
}

// =====================
// STOP EXAM
// =====================
function stopExam() {
    fetch("http://127.0.0.1:5000/stop_exam")
        .then(() => alert("Exam stopped"))
        .catch(err => console.error(err));
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
                scoreEl.innerText = data.score;
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
            if (alertBox && data.alert) {
                alertBox.innerText = data.alert;
            }
        })
        .catch(err => console.error(err));
}, 1500);

// =====================
// REAL TAB SWITCH DETECTION
// =====================
document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
        fetch("http://127.0.0.1:5000/tab_switched", {
            method: "POST"
        }).catch(err => console.error(err));

        alert("Warning: Tab switching detected!");
    }
});
