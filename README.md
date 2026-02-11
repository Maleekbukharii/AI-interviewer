# AI Interview Simulator 🎙️🤖

A premium, voice-enabled AI Mock Interview Simulator built with **FastAPI**, **OpenAI/OpenRouter**, and **Edge TTS**. Practice your interview skills with real-time feedback, technical scoring, and a sleek glassmorphic interface.

## ✨ Features

- **Real-time Voice Interaction**: Speak your answers and hear the interviewer respond naturally.
- **AI-Driven Interviewer**: Dynamic question generation based on your target company, position, and difficulty.
- **Smart Evaluation**: Get detailed scores (0-100) on Technical knowledge, Clarity, Structure, and Confidence.
- **Professionalism Guardrails**: Real-time alerts if your response is off-topic or unprofessional.
- **Coaching Feedback**: Personalized advice from an "AI Coach" after every answer.
- **Premium Design**: Modern, responsive glassmorphic UI with dark mode and smooth animations.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **Database**: SQLite with SQLAlchemy
- **AI Agents**: OpenAI GPT Models (via OpenRouter)
- **Voice Loop**:
  - **Speech-to-Text**: Whisper (Local transcription)
  - **Text-to-Speech**: Edge TTS (Microsoft Edge high-quality voices)
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (with `marked.js` for markdown rendering)

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- FFmpeg (Required for audio processing)

### 2. Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Maleekbukharii/AI-interviewer.git
   cd AI-interviewer
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/scripts/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If requirements.txt is missing, install the core packages:*
   `pip install fastapi uvicorn sqlalchemy openai edge-tts static-ffmpeg pydantic openai-whisper`

4. **Environment Setup**:
   Create a `.env` file in the root directory and add your API key:
   ```env
   OPENROUTER_API_KEY=your_openrouter_key_here
   ```

### 3. Running the App

Start the backend server:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Visit **`http://127.0.0.1:8000`** in your browser to start your interview!

## 📂 Project Structure

```text
├── backend/
│   ├── agents/          # AI Agent logic (Interviewer, Evaluator, Coach)
│   ├── db/              # Database models and session management
│   ├── services/        # Audio and Session services
│   ├── main.py          # FastAPI endpoints and orchestration
│   └── schemas.py       # Pydantic data models
├── frontend/
│   ├── app.js           # Frontend logic & API integration
│   ├── index.html       # UI Layout
│   └── style.css        # Glossy dark-theme styles
├── temp_audio/          # Generated speech cache (ignored by git)
└── README.md
```

## 📝 License
MIT License. Free to use and modify.
