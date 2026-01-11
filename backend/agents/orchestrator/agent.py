"""Orchestrator Agent - Coordinates multi-agent workflows"""
from agents.base_agent import BaseAgent
from services.agent_registry import register_agent, get_agents_by_skills
from agents.data_collection.agent import DataCollectionAgent
from agents.extraction.agent import ExtractionAgent
from agents.summarization.agent import SummarizationAgent
from agents.categorization.agent import CategorizationAgent
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

class OrchestratorAgent(BaseAgent):
    """Coordinates task assignment and agent workflows"""
    
    def __init__(self):
        super().__init__(
            agent_id="orchestrator_agent",
            agent_type="orchestrator",
            skills=["task_routing", "workflow_coordination", "agent_management"],
            capabilities={
                "input_types": ["task_request", "workflow_trigger"],
                "output_types": ["workflow_result", "task_assignment"]
            }
        )
        register_agent(
            self.agent_id,
            self.agent_type,
            self.skills,
            self.capabilities
        )
        
        # Initialize agent instances
        self.data_collection = DataCollectionAgent()
        self.extraction = ExtractionAgent()
        self.summarization = SummarizationAgent()
        self.categorization = CategorizationAgent()
    
    def process_meeting(self, meeting_text, location=None, audio_file=None, photo_files=None, user_id="default"):
        """Process a new meeting through the agent workflow"""
        self.update_status("busy")
        
        try:
            # Step 1: Data Collection
            logger.info("[ORCHESTRATOR] Step 1: Data Collection Agent")
            print("Step 1: Data Collection Agent")
            result = self.data_collection.process(meeting_text, location, audio_file, photo_files, user_id)
            person_id = result["person_id"]
            meeting_id = result["meeting_id"]
            unified_text = result.get("unified_text", meeting_text)  # Get unified text from data collection
            
            # Log unified text before calling extraction agent
            logger.info(f"[ORCHESTRATOR] ========== UNIFIED TEXT BEFORE EXTRACTION ==========")
            logger.info(f"[ORCHESTRATOR] Meeting ID: {meeting_id}")
            logger.info(f"[ORCHESTRATOR] Person ID: {person_id}")
            logger.info(f"[ORCHESTRATOR] Timestamp: {datetime.now().isoformat()}")
            logger.info(f"[ORCHESTRATOR] User ID: {user_id}")
            logger.info(f"[ORCHESTRATOR] Unified text length: {len(unified_text)} characters")
            logger.info(f"[ORCHESTRATOR] Unified text content:\n{unified_text}")
            logger.info(f"[ORCHESTRATOR] =====================================================")
            
            # Step 2: Information Extraction
            logger.info("[ORCHESTRATOR] Step 2: Extraction Agent")
            print("Step 2: Extraction Agent")
            self.extraction.extract(unified_text, person_id)  # Pass unified text to extraction
            
            # Step 3: Summarization
            logger.info("[ORCHESTRATOR] Step 3: Summarization Agent")
            print("Step 3: Summarization Agent")
            self.summarization.summarize(unified_text, meeting_id, user_id=user_id)  # Pass unified text
            
            # Step 4: Categorization
            logger.info("[ORCHESTRATOR] Step 4: Categorization Agent")
            print("Step 4: Categorization Agent")
            priority_group = self.categorization.categorize(person_id, meeting_id, user_id=user_id)
            
            self.update_status("idle")
            
            return {
                "person_id": person_id,
                "meeting_id": meeting_id,
                "priority_group": priority_group,
                "status": "completed"
            }
        
        except Exception as e:
            self.update_status("idle")
            print(f"Error in workflow: {e}")
            raise e
