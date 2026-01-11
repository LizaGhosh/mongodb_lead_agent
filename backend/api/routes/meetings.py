"""Meeting API routes"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
from agents.orchestrator.agent import OrchestratorAgent
from services.ocr import extract_text_from_image

router = APIRouter()
_orchestrator = None

def get_orchestrator():
    """Lazy initialization of orchestrator agent"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent()
    return _orchestrator

@router.post("/meetings")
async def create_meeting(
    text: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    photos: List[UploadFile] = File([]),
    user_id: Optional[str] = Form("default")
):
    """Submit a new meeting for processing with text, audio, and/or photos"""
    try:
        # Process photos if provided (for metadata)
        photo_text = None
        if photos:
            photo_names = [photo.filename for photo in photos]
            photo_text = f"[Photos uploaded: {', '.join(photo_names)}]"
        
        # Start with provided text
        meeting_text = (text or "").strip()
        
        # Audio transcription will be handled by Data Collection Agent
        # Photos will be processed by Data Collection Agent
        
        # Add photo metadata to text if provided
        if photo_text and meeting_text:
            meeting_text = f"{meeting_text}\n{photo_text}"
        elif photo_text:
            meeting_text = photo_text
        
        # At least one input must be provided
        if not meeting_text and not audio and not photos:
            raise HTTPException(status_code=400, detail="Please provide text, audio, or photos")
        
        orchestrator = get_orchestrator()
        result = orchestrator.process_meeting(
            meeting_text=meeting_text,
            location=location,
            audio_file=audio,
            photo_files=photos,
            user_id=user_id
        )
        
        # Get parsed inputs from the meeting record
        from database.connection import get_database
        from bson import ObjectId
        from datetime import datetime
        
        def convert_objectid(obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_objectid(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_objectid(item) for item in obj]
            return obj
        
        db = get_database()
        meeting = db.meetings.find_one({"meeting_id": result["meeting_id"]})
        person = db.people.find_one({"person_id": result["person_id"]})
        
        parsed_inputs = {
            "meeting_text": meeting_text,
            "location": location,
            "transcription": None,
            "ocr_texts": [],
            "raw_data": None
        }
        
        if meeting and meeting.get("raw_data"):
            raw_data = meeting["raw_data"]
            parsed_inputs["transcription"] = raw_data.get("transcribed_text")
            parsed_inputs["raw_data"] = convert_objectid(raw_data)
            
            # Extract OCR texts from photos
            if raw_data.get("photos"):
                for photo in raw_data["photos"]:
                    if photo.get("text_extracted") and photo.get("extracted_text"):
                        parsed_inputs["ocr_texts"].append({
                            "filename": photo.get("filename"),
                            "text": photo.get("extracted_text"),
                            "extracted_at": photo.get("extracted_at")
                        })
        
        return {
            "success": True,
            "meeting_id": result["meeting_id"],
            "person_id": result["person_id"],
            "priority_group": result["priority_group"],
            "parsed_inputs": parsed_inputs,
            "person": {
                "name": person.get("name") if person else None,
                "company": person.get("company") if person else None,
                "job_title": person.get("job_title") if person else None
            } if person else None,
            "meeting_date": meeting.get("date").isoformat() if meeting and meeting.get("date") else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ocr/extract")
async def extract_ocr_text(image: UploadFile = File(...)):
    """Extract text from an image using OCR"""
    try:
        extracted_text = extract_text_from_image(image)
        
        if extracted_text is None:
            return {
                "success": False,
                "text": "",
                "message": "Failed to extract text from image"
            }
        
        return {
            "success": True,
            "text": extracted_text,
            "message": "Text extracted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR error: {str(e)}")
