import edge_tts
import asyncio

# Voice model (Edge TTS has many high quality voices)
VOICE = "en-US-ChristopherNeural"

async def generate_audio(text: str, output_path: str = "output.wav"):
    """
    Generates audio from text using edge-tts (Async version).
    """
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(output_path)
        return output_path
    except Exception as e:
        return f"Error: {e}"

def generate_audio_sync(text: str, output_path: str = "output.wav"):
    """
    Generates audio from text using edge-tts (Sync wrapper).
    Use this in synchronous routes (def nodes).
    """
    try:
        asyncio.run(generate_audio(text, output_path))
        return output_path
    except Exception as e:
        # Fallback if asyncio.run fails (e.g. nested loops issue, though shouldn't happen in threads)
        return f"Error: {e}"
