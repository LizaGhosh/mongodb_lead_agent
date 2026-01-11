"""Base agent class with common functionality"""
from database.connection import get_database
from services.agent_registry import update_agent_status
from datetime import datetime
import uuid

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, agent_id, agent_type, skills, capabilities):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.skills = skills
        self.capabilities = capabilities
        self._db = None  # Lazy initialization
    
    @property
    def db(self):
        """Lazy database connection"""
        if self._db is None:
            self._db = get_database()
        return self._db
    
    def update_status(self, status, task_id=None):
        """Update agent status in MongoDB"""
        update_agent_status(self.agent_id, status, task_id)
    
    def get_task(self, task_type):
        """Get pending task of specific type"""
        task = self.db.tasks.find_one({
            "task_type": task_type,
            "status": "pending"
        })
        return task
    
    def update_task(self, task_id, status, output_data=None):
        """Update task status and output"""
        update = {
            "status": status,
            "updated_at": datetime.now()
        }
        
        if output_data:
            update["output_data"] = output_data
        
        self.db.tasks.update_one(
            {"task_id": task_id},
            {"$set": update}
        )
    
    def create_task(self, task_type, input_data, context_refs=None):
        """Create a new task"""
        task_id = str(uuid.uuid4())
        
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "assigned_agent_id": None,
            "status": "pending",
            "input_data": input_data,
            "output_data": {},
            "context_refs": context_refs or [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        self.db.tasks.insert_one(task)
        return task_id
