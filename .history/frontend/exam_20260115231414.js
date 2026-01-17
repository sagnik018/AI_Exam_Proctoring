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

