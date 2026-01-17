function startExam() {
    fetch("http://127.0.0.1:5000/start_exam")
        .then(response => {
            if (response.ok) {
                alert("Exam started with AI Proctoring");
            } else {
                alert("Failed to start exam");
            }
        })
        .catch(error => {
            alert("Backend not reachable. Is Flask running?");
            console.error(error);
        });
}
