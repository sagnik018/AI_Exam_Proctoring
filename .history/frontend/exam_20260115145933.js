function startExam() {
    fetch("/start_exam")
        .then(() => alert("Exam started with AI Proctoring"))
        .catch(err => alert("Error starting exam"));
}
