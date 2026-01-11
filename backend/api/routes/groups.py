"""Groups API routes"""
from fastapi import APIRouter, Query
from database.connection import get_database
from bson import ObjectId
from datetime import datetime

router = APIRouter()

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

@router.get("/groups")
async def get_groups(user_id: str = Query("default")):
    """Get all meetings grouped by priority (P0, P1, P2) for a specific user"""
    db = get_database()
    
    # Aggregate meetings grouped by priority_group
    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "priority_group": {"$in": ["P0", "P1", "P2"]},
                "status": "completed"
            }
        },
        {
            "$lookup": {
                "from": "people",
                "localField": "person_id",
                "foreignField": "person_id",
                "as": "person"
            }
        },
        {
            "$unwind": "$person"
        },
        {
            "$group": {
                "_id": "$priority_group",
                "meetings": {
                    "$push": {
                        "name": "$person.name",
                        "company": "$person.company",
                        "designation": "$person.job_title",
                        "summary": "$summary.text",
                        "meeting_date": "$date",
                        "meeting_timestamp": "$created_at",
                        "meeting_id": "$meeting_id"
                    }
                }
            }
        }
    ]
    
    results = list(db.meetings.aggregate(pipeline))
    
    # Format response and convert ObjectIds
    groups = {"P0": [], "P1": [], "P2": []}
    
    for result in results:
        priority = result["_id"]
        if priority in groups:
            meetings = convert_objectid(result["meetings"])
            groups[priority] = meetings
    
    return groups
