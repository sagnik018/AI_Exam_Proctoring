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

// STOP EXAM
function stopExam() {
    fetch("http://127.0.0.1:5000/stop_exam")
        .then(res => {
            if (res.ok) {
                alert("Exam stopped");
            }
        })
        .catch(err => console.error(err));
}

// UPDATE SUSPICION SCORE EVERY 2 SECONDS
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
