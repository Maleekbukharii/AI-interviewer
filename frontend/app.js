let mediaRecorder;
let audioChunks = [];
let sessionId = null;
let interviewComplete = false;

const startBtn = document.getElementById('start-btn');
const recordBtn = document.getElementById('record-btn');
const stopBtn = document.getElementById('stop-btn');
const setupArea = document.getElementById('setup-area');
const interviewArea = document.getElementById('interview-area');
const resultArea = document.getElementById('result-area');
const questionText = document.getElementById('current-question');
const feedbackArea = document.getElementById('feedback-area');
const coachText = document.getElementById('coach-text');

const audioPlayer = new Audio();
let timerInterval;
let seconds = 0;

function startTimer() {
    seconds = 0;
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        seconds++;
        const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
        const secs = String(seconds % 60).padStart(2, '0');
        document.getElementById('timer').innerText = `${mins}:${secs}`;
    }, 1000);
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            submitAudio(audioBlob);
        };

        mediaRecorder.start();
        recordBtn.parentElement.classList.add('recording');
        recordBtn.disabled = true;
        stopBtn.disabled = false;
        document.getElementById('record-text').innerText = "Recording Answer...";
    } catch (error) {
        console.error("Recording error:", error);
        alert("Microphone access denied or error: " + error.message);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        recordBtn.parentElement.classList.remove('recording');
        recordBtn.disabled = false;
        stopBtn.disabled = true;
        document.getElementById('record-text').innerText = "Record Answer";
    }
}

audioPlayer.onended = () => {
    if (!interviewComplete) {
        startRecording();
    }
};

startBtn.onclick = async () => {
    interviewComplete = false;
    const company = document.getElementById('company').value || "General";
    const position = document.getElementById('position').value || "Software Engineer";
    const difficulty = document.getElementById('difficulty').value;
    const questionLimit = parseInt(document.getElementById('question-limit').value) || 5;

    startBtn.disabled = true;
    startBtn.innerText = "Initializing Interview...";

    try {
        const response = await fetch('/start-interview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company, position, difficulty, question_limit: questionLimit })
        });

        const data = await response.json();
        sessionId = data.session_id;
        questionText.innerHTML = marked.parse(data.question);
        document.getElementById('session-info').innerText = `${company} | ${position} (${questionLimit} Questions)`;

        setupArea.style.display = 'none';
        interviewArea.style.display = 'flex';

        if (data.audio_url) {
            audioPlayer.src = data.audio_url;
            audioPlayer.play();
        }

        startTimer();
    } catch (error) {
        alert("Failed to start session. Please try again.");
    } finally {
        startBtn.disabled = false;
        startBtn.innerText = "Start Mock Interview";
    }
};

recordBtn.onclick = () => startRecording();

stopBtn.onclick = () => stopRecording();

async function submitAudio(blob) {
    const formData = new FormData();
    formData.append('audio_file', blob, 'answer.wav');
    formData.append('session_id', sessionId);

    questionText.innerText = "Deeply analyzing your response...";
    feedbackArea.style.display = 'none';

    try {
        const response = await fetch('/process-audio-turn', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(`Error: ${errorData.detail}`);
            questionText.innerText = "Error processing response. Please try again.";
            return;
        }

        const data = await response.json();

        // Update UI with turn feedback
        questionText.innerHTML = marked.parse(data.next_question);
        coachText.innerHTML = marked.parse(data.coach_feedback);
        feedbackArea.style.display = 'block';

        document.getElementById('score-tech').innerText = data.evaluation.technical_score + "%";
        document.getElementById('score-clarity').innerText = data.evaluation.clarity_score + "%";
        document.getElementById('score-structure').innerText = data.evaluation.structure_score + "%";
        document.getElementById('score-confidence').innerText = data.evaluation.confidence_score + "%";

        // Professionalism Check
        const warningBox = document.getElementById('warning-box');
        if (data.evaluation.professionalism_score < 70) {
            document.getElementById('warning-text').innerText = "Maintain a formal and focused tone for optimal results.";
            warningBox.style.display = 'block';
        } else {
            warningBox.style.display = 'none';
        }

        // Play audio
        if (data.audio_url) {
            audioPlayer.src = data.audio_url;
            audioPlayer.play();
        }

        // Final Report Check
        if (data.final_evaluation) {
            interviewComplete = true;
            setTimeout(() => displayFinalReport(data.final_evaluation), 2000);
        }
    } catch (error) {
        questionText.innerText = "Connection lost. Please check your internet.";
    }
}

function displayFinalReport(report) {
    interviewArea.style.display = 'none';
    resultArea.style.display = 'flex';

    document.getElementById('final-score').innerText = report.total_score + "%";
    document.getElementById('hiring-chances').innerText = report.hiring_chances;
    document.getElementById('final-summary').innerHTML = marked.parse(report.summary);

    window.scrollTo({ top: 0, behavior: 'smooth' });
}
