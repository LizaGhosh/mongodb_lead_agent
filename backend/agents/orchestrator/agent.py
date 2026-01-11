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
import uuid

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
        """Process a new meeting through the multi-agent workflow using task queue"""
        self.update_status("busy")
        
        try:
            # Create workflow ID to track all tasks
            workflow_id = str(uuid.uuid4())
            logger.info(f"[ORCHESTRATOR] Starting workflow {workflow_id}")
            
            # Step 1: Create Data Collection task (highest priority, no dependencies)
            data_collection_task_id = self.create_task(
                task_type="data_collection",
                input_data={
                    "meeting_text": meeting_text,
                    "location": location,
                    "audio_file": None,  # Will be handled separately due to file upload
                    "photo_files": None,  # Will be handled separately due to file upload
                    "user_id": user_id,
                    "workflow_id": workflow_id
                },
                priority=10  # Highest priority
            )
            logger.info(f"[ORCHESTRATOR] Created data_collection task: {data_collection_task_id}")
            
            # Files are passed directly to the workflow execution
            # (In a fully distributed system, files would be stored in object storage)
            result = self._execute_workflow(workflow_id, data_collection_task_id, audio_file, photo_files)
            
            self.update_status("idle")
            return result
        
        except Exception as e:
            self.update_status("idle")
            logger.error(f"[ORCHESTRATOR] Error in workflow: {e}")
            raise e
    
    def _execute_workflow(self, workflow_id, data_collection_task_id, audio_file=None, photo_files=None):
        """Execute workflow by having agents process tasks from queue"""
        import time
        
        # Step 1: Data Collection Agent processes task
        data_collection_task = self.db.tasks.find_one({"task_id": data_collection_task_id})
        if data_collection_task:
            # Claim and process
            if self.data_collection.claim_task(data_collection_task_id):
                logger.info("[ORCHESTRATOR] Data Collection Agent claimed task")
                result = self.data_collection.process_task(data_collection_task_id, audio_file, photo_files)
                person_id = result["person_id"]
                meeting_id = result["meeting_id"]
                unified_text = result.get("unified_text", "")
                
                # Step 2: Create Extraction task (depends on data collection)
                extraction_task_id = self.create_task(
                    task_type="extraction",
                    input_data={
                        "text": unified_text,
                        "person_id": person_id,
                        "workflow_id": workflow_id
                    },
                    depends_on=[data_collection_task_id],
                    priority=9
                )
                logger.info(f"[ORCHESTRATOR] Created extraction task: {extraction_task_id}")
                
                # Step 3: Create Summarization task (depends on data collection)
                summarization_task_id = self.create_task(
                    task_type="summarization",
                    input_data={
                        "text": unified_text,
                        "meeting_id": meeting_id,
                        "user_id": result.get("user_id", "default"),
                        "workflow_id": workflow_id
                    },
                    depends_on=[data_collection_task_id],
                    priority=8
                )
                logger.info(f"[ORCHESTRATOR] Created summarization task: {summarization_task_id}")
                
                # Step 4: Create Categorization task (depends on extraction and summarization)
                categorization_task_id = self.create_task(
                    task_type="categorization",
                    input_data={
                        "person_id": person_id,
                        "meeting_id": meeting_id,
                        "user_id": result.get("user_id", "default"),
                        "workflow_id": workflow_id
                    },
                    depends_on=[extraction_task_id, summarization_task_id],
                    priority=7
                )
                logger.info(f"[ORCHESTRATOR] Created categorization task: {categorization_task_id}")
                
                # Process remaining tasks
                # Extraction
                if self.extraction.claim_task(extraction_task_id):
                    logger.info("[ORCHESTRATOR] Extraction Agent claimed task")
                    self.extraction.process_task(extraction_task_id)
                
                # Summarization
                if self.summarization.claim_task(summarization_task_id):
                    logger.info("[ORCHESTRATOR] Summarization Agent claimed task")
                    self.summarization.process_task(summarization_task_id)
                
                # Wait for dependencies, then Categorization
                max_wait = 30  # seconds
                waited = 0
                while waited < max_wait:
                    extraction_done = self.db.tasks.find_one({"task_id": extraction_task_id, "status": "completed"})
                    summarization_done = self.db.tasks.find_one({"task_id": summarization_task_id, "status": "completed"})
                    if extraction_done and summarization_done:
                        break
                    time.sleep(0.5)
                    waited += 0.5
                
                if self.categorization.claim_task(categorization_task_id):
                    logger.info("[ORCHESTRATOR] Categorization Agent claimed task")
                    result = self.categorization.process_task(categorization_task_id)
                    priority_group = result.get("priority_group", "P2")
                else:
                    priority_group = "P2"
                
                return {
                    "person_id": person_id,
                    "meeting_id": meeting_id,
                    "priority_group": priority_group,
                    "status": "completed",
                    "workflow_id": workflow_id
                }
        
        raise Exception("Failed to process workflow")
