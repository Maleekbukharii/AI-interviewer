import whisper
import os
import static_ffmpeg

# Ensure ffmpeg is on the path
static_ffmpeg.add_paths()

_model = None

def get_model():
    global _model
    if _model is None:
        # Using "base" model as requested for balance of speed and accuracy
        print("Loading Whisper model...")
        _model = whisper.load_model("base")
    return _model

def transcribe_audio(file_path: str) -> str:
    if not os.path.exists(file_path):
        return "Error: File not found"
    
    model = get_model()
    result = model.transcribe(file_path)
    return result["text"].strip()
