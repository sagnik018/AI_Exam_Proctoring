function startExam() {
    fetch("http://127.0.0.1:5000/start_exam")
        .then(() => alert("Exam started with AI proctoring"))
        .catch(err => alert("Server not running"));
}
