"""Onboarding API routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database.connection import get_database
from services.preference_analysis import analyze_comments
from datetime import datetime
from bson import ObjectId

router = APIRouter()

class OnboardingRequest(BaseModel):
    use_case: str
    intent: str
    event_date: str
    event_location: str
    event_name: Optional[str] = None
    goals: str
    industries: List[str] = []
    company_sizes: List[str] = []
    job_titles: Optional[str] = None
    comments: Optional[str] = None

@router.post("/onboarding")
async def submit_onboarding(request: OnboardingRequest):
    """Submit onboarding form and save user preferences"""
    user_id = "default"  # Can be extended to support multiple users
    try:
        print(f"[ONBOARDING] Received onboarding request for user: {user_id}")
        print(f"[ONBOARDING] Request data: use_case={request.use_case}, intent={request.intent[:50] if request.intent else None}...")
        
        db = get_database()
        print(f"[ONBOARDING] Database connection established")
        
        # Analyze comments if provided
        extracted_preferences = {}
        if request.comments:
            print(f"[ONBOARDING] Analyzing comments (length: {len(request.comments)})")
            try:
                extracted_preferences = analyze_comments(request.comments)
                print(f"[ONBOARDING] Comments analyzed successfully")
            except Exception as e:
                print(f"[ONBOARDING] Error analyzing comments: {e}")
                extracted_preferences = {}
        
        # Process job_titles - handle empty strings properly
        job_titles_list = []
        if request.job_titles and request.job_titles.strip():
            job_titles_list = [title.strip() for title in request.job_titles.split(",") if title.strip()]
        
        # Build user preferences document
        user_prefs = {
            "user_id": user_id,
            "use_case": request.use_case,
            "intent": request.intent,
            "event_details": {
                "event_name": request.event_name,
                "event_date": request.event_date,
                "event_location": request.event_location
            },
            "goals": request.goals,
            "priorities": {
                "industries": request.industries,
                "company_sizes": request.company_sizes,
                "job_titles": job_titles_list
            },
            "extracted_preferences": extracted_preferences,
            "onboarding_comments": request.comments,
            "preference_analysis": {
                "processed_at": datetime.now().isoformat(),
                "extracted_entities": extracted_preferences.get("custom_criteria", []),
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        print(f"[ONBOARDING] Saving user preferences to database")
        # Save or update user preferences
        result = db.user_preferences.update_one(
            {"user_id": user_id},
            {"$set": user_prefs},
            upsert=True
        )
        print(f"[ONBOARDING] Preferences saved successfully. Upserted: {result.upserted_id}, Modified: {result.modified_count}")
        
        return {
            "success": True,
            "message": "Preferences saved successfully",
            "user_id": user_id
        }
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ONBOARDING] Error processing onboarding request: {str(e)}")
        print(f"[ONBOARDING] Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error saving preferences: {str(e)}")

def convert_objectid(obj):
    """Convert ObjectId and datetime to JSON-serializable types"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    return obj

@router.get("/onboarding/{user_id}")
async def get_onboarding_status(user_id: str):
    """Check if user has completed onboarding"""
    try:
        db = get_database()
        user_prefs = db.user_preferences.find_one({"user_id": user_id})
        
        # Convert ObjectId to string for JSON serialization
        preferences = None
        if user_prefs:
            preferences = convert_objectid(user_prefs)
        
        return {
            "completed": user_prefs is not None,
            "preferences": preferences
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
