"""Initialize MongoDB database with collections and indexes"""
import sys
import os

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_database

def setup_database():
    """Create collections and indexes"""
    db = get_database()
    
    # Collections will be created automatically on first insert
    # But we can ensure they exist and create indexes
    
    # Agents collection
    db.agents.create_index("agent_id", unique=True)
    db.agents.create_index("status")
    db.agents.create_index("skills")
    
    # Tasks collection
    db.tasks.create_index("task_id", unique=True)
    db.tasks.create_index("status")
    db.tasks.create_index("assigned_agent_id")
    
    # People collection
    db.people.create_index("person_id", unique=True)
    db.people.create_index("meeting_ids")
    
    # Meetings collection
    db.meetings.create_index("meeting_id", unique=True)
    db.meetings.create_index("person_id")
    db.meetings.create_index("priority_group")
    db.meetings.create_index("date")
    
    # User preferences collection
    db.user_preferences.create_index("user_id", unique=True)
    
    # Contexts collection
    db.contexts.create_index("context_id", unique=True)
    db.contexts.create_index("person_id")
    db.contexts.create_index("meeting_id")
    
    # Agent communications collection
    db.agent_communications.create_index("communication_id", unique=True)
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
