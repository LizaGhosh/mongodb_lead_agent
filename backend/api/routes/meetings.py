"""Meeting API routes"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
from agents.orchestrator.agent import OrchestratorAgent
from services.ocr import extract_text_from_image
import logging

logger = logging.getLogger(__name__)

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
    # Use print() for Vercel logs - these will appear in Vercel dashboard
    print("=" * 80)
    print("[MEETINGS] New meeting submission received")
    print(f"[MEETINGS] User ID: {user_id}")
    print(f"[MEETINGS] Has text: {bool(text)}, Length: {len(text) if text else 0}")
    print(f"[MEETINGS] Has audio: {audio is not None}")
    if audio:
        print(f"[MEETINGS] Audio file: {audio.filename}, Size: {audio.size if hasattr(audio, 'size') else 'unknown'}")
    print(f"[MEETINGS] Photo count: {len(photos)}")
    if photos:
        for i, photo in enumerate(photos):
            print(f"[MEETINGS] Photo {i+1}: {photo.filename}, Size: {photo.size if hasattr(photo, 'size') else 'unknown'}")
    print(f"[MEETINGS] Location: {location}")
    
    # Also use logger for consistency
    logger.info("=" * 80)
    logger.info("[MEETINGS] New meeting submission received")
    logger.info(f"[MEETINGS] User ID: {user_id}")
    
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
            print("[MEETINGS] ❌ Validation failed: No input provided")
            raise HTTPException(status_code=400, detail="Please provide text, audio, or photos")
        
        print("[MEETINGS] Starting orchestrator processing...")
        orchestrator = get_orchestrator()
        result = orchestrator.process_meeting(
            meeting_text=meeting_text,
            location=location,
            audio_file=audio,
            photo_files=photos,
            user_id=user_id
        )
        print(f"[MEETINGS] Orchestrator processing completed")
        
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
        
        print(f"[MEETINGS] ✅ Success! Meeting ID: {result['meeting_id']}, Person ID: {result['person_id']}")
        print(f"[MEETINGS] Priority Group: {result.get('priority_group', 'N/A')}")
        logger.info(f"[MEETINGS] Successfully processed meeting: {result['meeting_id']}")
        
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
        import traceback
        # Print error details for Vercel logs
        print(f"[MEETINGS] ❌ ERROR OCCURRED")
        print(f"[MEETINGS] Error Type: {type(e).__name__}")
        print(f"[MEETINGS] Error Message: {str(e)}")
        print(f"[MEETINGS] Full Traceback:")
        print(traceback.format_exc())
        print("=" * 80)
        
        logger.error(f"[MEETINGS] Error processing meeting: {str(e)}", exc_info=True)
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
        import traceback
        print(f"[OCR] ❌ ERROR OCCURRED")
        print(f"[OCR] Error Type: {type(e).__name__}")
        print(f"[OCR] Error Message: {str(e)}")
        print(f"[OCR] Full Traceback:")
        print(traceback.format_exc())
        logger.error(f"[OCR] Error extracting text: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"OCR error: {str(e)}")
