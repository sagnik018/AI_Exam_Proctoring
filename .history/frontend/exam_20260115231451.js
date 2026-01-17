// START EXAM
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

function stopExam() {
    fetch("http://127.0.0.1:5000/stop_exam")
        .then(() => alert("Exam stopped"));
}

// Update suspicion score
setInterval(() => {
    fetch("http://127.0.0.1:5000/suspicion_score")
        .then(res => res.json())
        .then(data => {
            document.getElementById("score").innerText = data.score;
        });
}, 2000);

// Show alert messages in UI
setInterval(() => {
    fetch("http://127.0.0.1:5000/latest_alert")
        .then(res => res.json())
        .then(data => {
            if (data.alert) {
                document.getElementById("alertBox").innerText = data.alert;
            }
        });
}, 1500);
