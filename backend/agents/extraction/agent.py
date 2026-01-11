"""Information Extraction Agent - Extracts structured data from text"""
from agents.base_agent import BaseAgent
from services.agent_registry import register_agent
from services.prompt_loader import load_prompt, format_prompt
from config.settings import OPENAI_API_KEY
from openai import OpenAI
from datetime import datetime
import json

class ExtractionAgent(BaseAgent):
    """Extracts structured information from meeting text"""
    
    def __init__(self):
        super().__init__(
            agent_id="extraction_agent",
            agent_type="extraction",
            skills=["entity_extraction", "nlp", "data_normalization"],
            capabilities={
                "input_types": ["text", "structured_data"],
                "output_types": ["person_profile", "extracted_entities"]
            }
        )
        register_agent(
            self.agent_id,
            self.agent_type,
            self.skills,
            self.capabilities
        )
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        # Load prompts from YAML
        self.prompt_config = load_prompt("extraction.yaml")
    
    def extract(self, text, person_id):
        """Extract entities from text"""
        self.update_status("busy")
        
        try:
            if not self.client:
                # Fallback: simple extraction
                return self._simple_extract(text, person_id)
            
            # Use OpenAI to extract information
            # Load prompt from YAML and format it
            user_prompt = format_prompt(
                self.prompt_config["user_prompt_template"],
                text=text
            )

            response = self.client.chat.completions.create(
                model=self.prompt_config["model"],
                messages=[
                    {"role": "system", "content": self.prompt_config["system_message"]},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.prompt_config["temperature"]
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                extracted = json.loads(result_text)
            except:
                # If not valid JSON, try to extract from text
                extracted = self._simple_extract(text, person_id)
            
            # Update person document
            self.db.people.update_one(
                {"person_id": person_id},
                {
                    "$set": {
                        "name": extracted.get("name"),
                        "company": extracted.get("company"),
                        "job_title": extracted.get("job_title"),
                        "extracted_data": {
                            "contact_info": extracted.get("contact_info", {}),
                            "extracted_at": datetime.now()
                        }
                    }
                }
            )
            
            self.update_status("idle")
            return extracted
        
        except Exception as e:
            self.update_status("idle")
            # Fallback to simple extraction
            return self._simple_extract(text, person_id)
    
    def _simple_extract(self, text, person_id):
        """Simple fallback extraction"""
        from datetime import datetime
        
        # Very basic extraction (for demo)
        extracted = {
            "name": "Unknown",
            "company": "Unknown",
            "job_title": "Unknown",
            "contact_info": {}
        }
        
        # Update person with basic info
        self.db.people.update_one(
            {"person_id": person_id},
            {
                "$set": {
                    "name": extracted["name"],
                    "company": extracted["company"],
                    "job_title": extracted["job_title"],
                    "extracted_data": {
                        "contact_info": extracted["contact_info"],
                        "extracted_at": datetime.now()
                    }
                }
            }
        )
        
        return extracted
    
    def process_task(self, task_id):
        """Process a task from the queue"""
        task = self.db.tasks.find_one({"task_id": task_id})
        if not task:
            raise Exception(f"Task {task_id} not found")
        
        self.update_status("busy", task_id)
        
        try:
            input_data = task.get("input_data", {})
            text = input_data.get("text", "")
            person_id = input_data.get("person_id")
            
            if not person_id:
                raise Exception("person_id not found in task input")
            
            # Extract information
            result = self.extract(text, person_id)
            
            # Update task with results
            self.update_task(task_id, "completed", {
                "person_id": person_id,
                "extracted_data": result
            })
            
            self.update_status("idle")
            return result
        
        except Exception as e:
            self.update_task(task_id, "failed", {"error": str(e)})
            self.update_status("idle")
            raise e