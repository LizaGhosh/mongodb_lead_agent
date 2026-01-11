"""Data Collection Agent - Processes meeting input and creates initial records"""
from agents.base_agent import BaseAgent
from services.agent_registry import register_agent
from services.transcription import transcribe_audio
from services.ocr import extract_text_from_image
from datetime import datetime
import uuid
import logging

class DataCollectionAgent(BaseAgent):
    """Processes meeting data and creates person/meeting records"""
    
    def __init__(self):
        super().__init__(
            agent_id="data_collection_agent",
            agent_type="data_collection",
            skills=["voice_processing", "image_processing", "data_validation"],
            capabilities={
                "input_types": ["text", "voice", "image"],
                "output_types": ["person_profile", "meeting_record"]
            }
        )
        register_agent(
            self.agent_id,
            self.agent_type,
            self.skills,
            self.capabilities
        )
    
    def process(self, meeting_text, location=None, audio_file=None, photo_files=None, user_id="default"):
        """Process meeting input and create records"""
        self.update_status("busy")
        logger = logging.getLogger(__name__)
        
        try:
            # Create person ID
            person_id = str(uuid.uuid4())
            meeting_id = str(uuid.uuid4())
            
            # Process audio file if provided - transcribe it
            audio_data = None
            transcribed_text = None
            if audio_file:
                logger.info(f"[DATA_COLLECTION] Processing audio file: {audio_file.filename}")
                
                transcribed_text = transcribe_audio(audio_file)
                
                audio_data = {
                    "filename": audio_file.filename,
                    "content_type": audio_file.content_type,
                    "size": audio_file.size if hasattr(audio_file, 'size') else None,
                    "transcribed": transcribed_text is not None,
                    "transcribed_at": datetime.now().isoformat() if transcribed_text else None
                }
                
                if transcribed_text:
                    logger.info(f"[DATA_COLLECTION] Transcription successful: {len(transcribed_text)} characters")
                    # Combine transcribed text with existing text
                    if meeting_text:
                        meeting_text = f"{meeting_text}\n\n[Audio Transcription]\n{transcribed_text}"
                    else:
                        meeting_text = transcribed_text
                else:
                    logger.warning("[DATA_COLLECTION] Transcription failed or skipped")
            
            # Process photo files if provided - extract text using OCR
            photo_data = []
            photo_texts = []
            if photo_files:
                logger.info(f"[DATA_COLLECTION] Processing {len(photo_files)} photo(s)")
                for photo in photo_files:
                    logger.info(f"[DATA_COLLECTION] Extracting text from: {photo.filename}")
                    extracted_text = extract_text_from_image(photo)
                    
                    photo_info = {
                        "filename": photo.filename,
                        "content_type": photo.content_type,
                        "size": photo.size if hasattr(photo, 'size') else None,
                        "text_extracted": extracted_text is not None,
                        "extracted_text": extracted_text,  # Store the actual OCR text
                        "extracted_at": datetime.now().isoformat() if extracted_text else None
                    }
                    photo_data.append(photo_info)
                    
                    if extracted_text:
                        photo_texts.append(f"[Text from {photo.filename}]\n{extracted_text}")
                        logger.info(f"[DATA_COLLECTION] OCR successful for {photo.filename}: {len(extracted_text)} characters")
                    else:
                        logger.warning(f"[DATA_COLLECTION] OCR failed for {photo.filename}")
                
                # Combine extracted text from all photos with meeting text
                if photo_texts:
                    photos_text = "\n\n".join(photo_texts)
                    if meeting_text:
                        meeting_text = f"{meeting_text}\n\n{photos_text}"
                    else:
                        meeting_text = photos_text
            
            # Create person document
            person = {
                "person_id": person_id,
                "name": None,  # Will be filled by extraction agent
                "company": None,
                "job_title": None,
                "extracted_data": {},
                "categorization": {},
                "meeting_ids": [meeting_id],
                "created_at": datetime.now()
            }
            
            # Create meeting document
            meeting = {
                "meeting_id": meeting_id,
                "person_id": person_id,
                "user_id": user_id,  # Store user_id for preference lookup
                "date": datetime.now(),
                "location": location or "Unknown",
                "raw_data": {
                    "text": meeting_text,
                    "audio": audio_data,
                    "photos": photo_data,
                    "transcribed_text": transcribed_text  # Store transcription separately
                },
                "summary": {},
                "priority_group": None,
                "status": "processing",
                "created_at": datetime.now()
            }
            
            # Store in MongoDB
            self.db.people.insert_one(person)
            self.db.meetings.insert_one(meeting)
            
            # Log unified text with timestamp
            logger.info(f"[DATA_COLLECTION] Unified text created for meeting_id: {meeting_id}")
            logger.info(f"[DATA_COLLECTION] Timestamp: {datetime.now().isoformat()}")
            logger.info(f"[DATA_COLLECTION] Unified text length: {len(meeting_text)} characters")
            logger.info(f"[DATA_COLLECTION] Unified text content:\n{'='*80}\n{meeting_text}\n{'='*80}")
            
            self.update_status("idle")
            
            return {
                "person_id": person_id,
                "meeting_id": meeting_id,
                "unified_text": meeting_text  # Return unified text for logging in orchestrator
            }
        
        except Exception as e:
            self.update_status("idle")
            raise e
    
    def process_task(self, task_id, audio_file=None, photo_files=None):
        """Process a task from the queue"""
        task = self.db.tasks.find_one({"task_id": task_id})
        if not task:
            raise Exception(f"Task {task_id} not found")
        
        self.update_status("busy", task_id)
        
        try:
            input_data = task.get("input_data", {})
            meeting_text = input_data.get("meeting_text", "")
            location = input_data.get("location")
            user_id = input_data.get("user_id", "default")
            
            # Process the meeting
            result = self.process(meeting_text, location, audio_file, photo_files, user_id)
            
            # Update task with results
            self.update_task(task_id, "completed", {
                "person_id": result["person_id"],
                "meeting_id": result["meeting_id"],
                "unified_text": result.get("unified_text", meeting_text),
                "user_id": user_id
            })
            
            self.update_status("idle")
            return result
        
        except Exception as e:
            self.update_task(task_id, "failed", {"error": str(e)})
            self.update_status("idle")
            raise e