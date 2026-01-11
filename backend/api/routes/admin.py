"""Admin API routes for database management"""
from fastapi import APIRouter, HTTPException
from database.connection import get_database

router = APIRouter()

@router.delete("/admin/clear-data")
async def clear_all_data():
    """Clear all data from the database (people, meetings, tasks, contexts, etc.)"""
    try:
        db = get_database()
        
        # Clear all collections
        result = {
            "people_deleted": db.people.delete_many({}).deleted_count,
            "meetings_deleted": db.meetings.delete_many({}).deleted_count,
            "tasks_deleted": db.tasks.delete_many({}).deleted_count,
            "contexts_deleted": db.contexts.delete_many({}).deleted_count,
            "agent_communications_deleted": db.agent_communications.delete_many({}).deleted_count,
        }
        
        # Note: We keep agents and user_preferences collections intact
        
        return {
            "success": True,
            "message": "All data cleared successfully",
            "deleted_counts": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/reset-onboarding/{user_id}")
async def reset_onboarding(user_id: str):
    """Reset onboarding for a user (delete their preferences)"""
    try:
        db = get_database()
        result = db.user_preferences.delete_one({"user_id": user_id})
        
        return {
            "success": True,
            "message": "Onboarding reset successfully",
            "deleted_count": result.deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
