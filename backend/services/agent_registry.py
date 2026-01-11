"""Agent registry service for managing agent registration and discovery"""
from database.connection import get_database
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def register_agent(agent_id, agent_type, skills, capabilities):
    """Register an agent in MongoDB"""
    try:
        db = get_database()
        
        agent_doc = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "skills": skills,
            "capabilities": capabilities,
            "status": "idle",
            "current_task_id": None,
            "registered_at": datetime.now(),
            "last_heartbeat": datetime.now()
        }
        
        db.agents.update_one(
            {"agent_id": agent_id},
            {"$set": agent_doc},
            upsert=True
        )
        
        logger.info(f"Agent {agent_id} registered")
        print(f"Agent {agent_id} registered")
    except Exception as e:
        logger.error(f"Failed to register agent {agent_id}: {e}")
        # Don't raise - allow the app to start even if registration fails
        # The connection will be retried when actually needed
        print(f"Warning: Failed to register agent {agent_id} (MongoDB connection may not be ready): {e}")


def get_agents_by_skills(required_skills, status="idle"):
    """Find agents with required skills"""
    db = get_database()
    
    agents = db.agents.find({
        "skills": {"$in": required_skills},
        "status": status
    })
    
    return list(agents)


def update_agent_status(agent_id, status, task_id=None):
    """Update agent status"""
    db = get_database()
    
    update = {
        "status": status,
        "last_heartbeat": datetime.now()
    }
    
    if task_id is not None:
        update["current_task_id"] = task_id
    
    db.agents.update_one(
        {"agent_id": agent_id},
        {"$set": update}
    )
