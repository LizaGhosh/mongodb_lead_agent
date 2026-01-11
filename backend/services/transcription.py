"""Audio transcription service using OpenAI Whisper API"""
from config.settings import OPENAI_API_KEY
from openai import OpenAI
import io
import logging
from datetime import datetime

# Set up logger
logger = logging.getLogger(__name__)

def transcribe_audio(audio_file):
    """
    Transcribe audio file using OpenAI Whisper API
    
    Args:
        audio_file: FastAPI UploadFile object
        
    Returns:
        str: Transcribed text or None if transcription fails
    """
    start_time = datetime.now()
    filename = audio_file.filename or "unknown"
    
    logger.info(f"[TRANSCRIPTION] Starting transcription for file: {filename}")
    
    if not OPENAI_API_KEY:
        logger.warning("[TRANSCRIPTION] OPENAI_API_KEY not set. Skipping transcription.")
        return None
    
    try:
        logger.info(f"[TRANSCRIPTION] Initializing OpenAI client for file: {filename}")
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Read audio file content
        logger.info(f"[TRANSCRIPTION] Reading audio file content: {filename}")
        audio_content = audio_file.file.read()
        file_size = len(audio_content)
        logger.info(f"[TRANSCRIPTION] Audio file size: {file_size} bytes ({file_size/1024:.2f} KB)")
        
        # Reset file pointer for potential reuse
        audio_file.file.seek(0)
        
        # Create a file-like object for OpenAI API
        audio_file_obj = io.BytesIO(audio_content)
        audio_file_obj.name = filename
        
        # Transcribe using Whisper API
        logger.info(f"[TRANSCRIPTION] Sending audio to Whisper API: {filename}")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file_obj,
            language="en"  # Optional: specify language
        )
        
        transcribed_text = transcript.text
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"[TRANSCRIPTION] Successfully transcribed: {filename}")
        logger.info(f"[TRANSCRIPTION] Transcription length: {len(transcribed_text)} characters")
        logger.info(f"[TRANSCRIPTION] Transcription time: {duration:.2f} seconds")
        logger.info(f"[TRANSCRIPTION] Transcribed text preview: {transcribed_text[:100]}...")
        
        return transcribed_text
    
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"[TRANSCRIPTION] Error transcribing audio file {filename}: {str(e)}")
        logger.error(f"[TRANSCRIPTION] Transcription failed after {duration:.2f} seconds")
        return None
