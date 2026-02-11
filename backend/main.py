from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .db.database import SessionLocal, InterviewSession, InterviewLog
from .schemas import InterviewStart, UserAnswer, Evaluation
from .agents.interviewer import Interviewer
from .agents.evaluator import Evaluator
from .agents.coach import Coach
from .services.speech_to_text import transcribe_audio
from .services.text_to_speech import generate_audio, generate_audio_sync
from .services.session_manager import SessionManager
import uuid
import os
import openai
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

class TextToSpeak(BaseModel):
    text: str

app = FastAPI(title="AI Interview Simulator")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize Agents
interviewer = Interviewer()
evaluator = Evaluator()
coach = Coach()

# Audio config
AUDIO_DIR = "temp_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.post("/start-interview")
def start_interview(data: InterviewStart, db: Session = Depends(get_db)):
    sm = SessionManager(db)
    session = sm.create_session(data.company, data.position, data.difficulty)
    
    context = f"Company: {data.company}, Position: {data.position}, Difficulty: {data.difficulty}"
    first_question = interviewer.get_next_question(history="", context=context)
    
    sm.update_history(session.id, f"Interviewer: {first_question}\n")
    
    # Generate audio for the first question
    filename = f"speech_{uuid.uuid4()}.wav"
    speech_output = os.path.join(AUDIO_DIR, filename)
    generate_audio_sync(first_question, speech_output)
    
    return {
        "session_id": session.id, 
        "question": first_question,
        "audio_url": f"/audio/{filename}"
    }

@app.post("/submit-answer")
def submit_answer(data: UserAnswer, db: Session = Depends(get_db)):
    sm = SessionManager(db)
    session = sm.get_session(data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history_lines = session.history.strip().split("\n")
    last_question = history_lines[-1].replace("Interviewer: ", "") if history_lines else ""
    
    eval_result = evaluator.evaluate_answer(last_question, data.answer_text)
    coaching_feedback = coach.get_feedback(eval_result.model_dump_json())
    
    sm.update_history(session.id, f"User: {data.answer_text}\n")
    sm.log_turn(session.id, last_question, data.answer_text, eval_result)
    
    context = f"Company: {session.company}, Position: {session.position}, Difficulty: {session.difficulty}"
    next_question = interviewer.get_next_question(history=session.history, context=context)
    
    sm.update_history(session.id, f"Interviewer: {next_question}\n")
    
    return {
        "evaluation": eval_result,
        "coach_feedback": coaching_feedback,
        "next_question": next_question
    }

@app.get("/session/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    sm = SessionManager(db)
    session = sm.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    logs = sm.get_logs(session_id)
    
    return {
        "session": session,
        "logs": logs
    }

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Save temp file
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    try:
        text = transcribe_audio(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return {"text": text}

@app.post("/speak")
async def speak(data: TextToSpeak):
    filename = f"speech_{uuid.uuid4()}.wav"
    output_path = os.path.join(AUDIO_DIR, filename)
    result = await generate_audio(data.text, output_path)
    
    if result.startswith("Error"):
        raise HTTPException(status_code=500, detail=result)
        
    return FileResponse(output_path, media_type="audio/wav", filename="speech.wav")

@app.post("/process-audio-turn")
async def process_audio_turn(
    session_id: str = File(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    sm = SessionManager(db)
    
    # 1. Transcribe
    temp_audio = f"temp_{uuid.uuid4()}_{audio_file.filename}"
    with open(temp_audio, "wb") as f:
        f.write(await audio_file.read())
    
    try:
        user_text = transcribe_audio(temp_audio)
    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

    # 2. Process turn
    session = sm.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history_lines = session.history.strip().split("\n")
    last_question = history_lines[-1].replace("Interviewer: ", "") if history_lines else ""
    
    try:
        eval_result = evaluator.evaluate_answer(last_question, user_text)
        coaching_feedback = coach.get_feedback(eval_result.model_dump_json())
        
        sm.update_history(session.id, f"User: {user_text}\n")
        sm.log_turn(session.id, last_question, user_text, eval_result)
        
        context = f"Company: {session.company}, Position: {session.position}, Difficulty: {session.difficulty}"
        next_question = interviewer.get_next_question(history=session.history, context=context)
        sm.update_history(session.id, f"Interviewer: {next_question}\n")
    except openai.RateLimitError:
        raise HTTPException(status_code=429, detail="API Rate Limit Exceeded. Please check your API credits or try again later.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Agent Error: {str(e)}")

    # 3. Speak (Next Question)
    # Clean text for TTS (remove markdown asterisks etc)
    import re
    def clean_text_for_tts(text: str) -> str:
        # Remove bold/italic markdown (**text** or *text*)
        text = re.sub(r'\*+(.*?)\*+', r'\1', text)
        # Remove markdown links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove other common markdown symbols
        text = text.replace("#", "").replace("`", "")
        return text

    clean_question = clean_text_for_tts(next_question)

    filename = f"speech_{uuid.uuid4()}.wav"
    speech_output = os.path.join(AUDIO_DIR, filename)
    await generate_audio(clean_question, speech_output)

    return {
        "user_text": user_text,
        "evaluation": eval_result,
        "coach_feedback": coaching_feedback,
        "next_question": next_question,
        "audio_url": f"/audio/{filename}"
    }

# Serve static files from the 'frontend' directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("frontend/index.html")

# Serve audio files from the dedicated directory
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# We also need to serve the CSS/JS if they are referenced via relative paths in HTML
# Currently index.html uses "style.css" and "app.js"
# I'll mount the frontend directory directly at / as well to catch these
app.mount("/", StaticFiles(directory="frontend"), name="frontend_root")
