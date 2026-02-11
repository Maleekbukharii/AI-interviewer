let mediaRecorder;
let audioChunks = [];
let sessionId = null;

const startBtn = document.getElementById('start-btn');
const recordBtn = document.getElementById('record-btn');
const stopBtn = document.getElementById('stop-btn');
const setupArea = document.getElementById('setup-area');
const interviewArea = document.getElementById('interview-area');
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

startBtn.onclick = async () => {
    const company = document.getElementById('company').value || "General";
    const position = document.getElementById('position').value || "Software Engineer";
    const difficulty = document.getElementById('difficulty').value;

    const response = await fetch('/start-interview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company, position, difficulty })
    });

    const data = await response.json();
    sessionId = data.session_id;
    questionText.innerHTML = marked.parse(data.question);
    document.getElementById('session-info').innerText = `${company} | ${position}`;

    setupArea.style.display = 'none';
    interviewArea.style.display = 'flex';

    if (data.audio_url) {
        audioPlayer.src = data.audio_url;
        audioPlayer.play();
    }

    startTimer();
};

recordBtn.onclick = async () => {
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
    document.getElementById('record-text').innerText = "Recording...";
};

stopBtn.onclick = () => {
    mediaRecorder.stop();
    recordBtn.parentElement.classList.remove('recording');
    recordBtn.disabled = false;
    stopBtn.disabled = true;
    document.getElementById('record-text').innerText = "Record Answer";
};

async function submitAudio(blob) {
    const formData = new FormData();
    formData.append('audio_file', blob, 'answer.wav');
    formData.append('session_id', sessionId);

    questionText.innerText = "Processing your answer...";
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
            recordBtn.disabled = false;
            return;
        }

        const data = await response.json();

        // Update UI
        questionText.innerHTML = marked.parse(data.next_question);
        coachText.innerHTML = marked.parse(data.coach_feedback);
        feedbackArea.style.display = 'block';

        document.getElementById('score-tech').innerText = data.evaluation.technical_score + " / 100";
        document.getElementById('score-clarity').innerText = data.evaluation.clarity_score + " / 100";
        document.getElementById('score-structure').innerText = data.evaluation.structure_score + " / 100";
        document.getElementById('score-confidence').innerText = data.evaluation.confidence_score + " / 100";

        // Dynamic professionalism check
        const warningBox = document.getElementById('warning-box');
        if (data.evaluation.professionalism_score < 70) {
            document.getElementById('warning-text').innerText = "Your response seems off-topic or unprofessional. Please stay focused on the interview context.";
            warningBox.style.display = 'block';
        } else {
            warningBox.style.display = 'none';
        }

        // Play the next question
        if (data.audio_url) {
            audioPlayer.src = data.audio_url;
            audioPlayer.play();
        }
    } catch (error) {
        console.error("Error processing turn:", error);
        questionText.innerText = "Error processing answer. Please try again.";
    }
}
