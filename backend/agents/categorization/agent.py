"""Categorization Agent - Groups contacts into P0, P1, P2"""
from agents.base_agent import BaseAgent
from services.agent_registry import register_agent
from services.prompt_loader import load_prompt, format_prompt
from config.settings import OPENAI_API_KEY
from openai import OpenAI
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class CategorizationAgent(BaseAgent):
    """Categorizes contacts by priority (P0, P1, P2)"""
    
    def __init__(self):
        super().__init__(
            agent_id="categorization_agent",
            agent_type="categorization",
            skills=["scoring", "categorization", "priority_assignment"],
            capabilities={
                "input_types": ["person_profile", "meeting_data"],
                "output_types": ["priority_group", "score"]
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
        self.prompt_config = load_prompt("categorization.yaml")
    
    def categorize(self, person_id, meeting_id, user_id="default"):
        """Categorize contact into P0, P1, or P2 using AI-based scoring"""
        self.update_status("busy")
        
        try:
            # Get person and meeting data
            person = self.db.people.find_one({"person_id": person_id})
            meeting = self.db.meetings.find_one({"meeting_id": meeting_id})
            
            if not person or not meeting:
                raise ValueError("Person or meeting not found")
            
            # Get user preferences
            user_prefs = self._get_user_preferences(user_id)
            
            # Get conversation text (unified text from meeting)
            conversation_text = meeting.get("raw_data", {}).get("text", "")
            summary = meeting.get("summary", {}).get("text", "")
            
            # Use AI-based scoring if OpenAI is available
            if self.client:
                result = self._ai_categorize(
                    person=person,
                    meeting=meeting,
                    conversation_text=conversation_text,
                    summary=summary,
                    user_prefs=user_prefs
                )
            else:
                # Fallback to simple scoring
                logger.warning("[CATEGORIZATION] OpenAI not available, using fallback scoring")
                result = self._simple_categorize(person, meeting)
            
            # Update person document
            self.db.people.update_one(
                {"person_id": person_id},
                {
                    "$set": {
                        "categorization": {
                            "score": result["score"],
                            "priority_group": result["priority_group"],
                            "reasons": result.get("reasons", []),
                            "persona": result.get("persona", ""),
                            "urgency_level": result.get("urgency_level", ""),
                            "intent_match_score": result.get("intent_match_score", 0.0),
                            "categorized_at": datetime.now()
                        }
                    }
                }
            )
            
            # Update meeting document
            self.db.meetings.update_one(
                {"meeting_id": meeting_id},
                {
                    "$set": {
                        "priority_group": result["priority_group"],
                        "status": "completed"
                    }
                }
            )
            
            self.update_status("idle")
            return result["priority_group"]
        
        except Exception as e:
            logger.error(f"[CATEGORIZATION] Error categorizing contact: {e}", exc_info=True)
            self.update_status("idle")
            # Fallback to simple categorization
            return self._simple_categorize(person, meeting)["priority_group"]
    
    def _get_user_preferences(self, user_id):
        """Get user preferences from onboarding form"""
        try:
            user_prefs = self.db.user_preferences.find_one({"user_id": user_id})
            if not user_prefs:
                return {
                    "use_case": "networking",
                    "intent": "",
                    "goals": "",
                    "industries": [],
                    "company_sizes": [],
                    "job_titles": [],
                    "custom_criteria": [],
                    "value_indicators": []
                }
            
            extracted = user_prefs.get("extracted_preferences", {})
            priorities = user_prefs.get("priorities", {})
            
            return {
                "use_case": user_prefs.get("use_case", "networking"),
                "intent": user_prefs.get("intent", ""),
                "goals": user_prefs.get("goals", ""),
                "industries": priorities.get("industries", []),
                "company_sizes": priorities.get("company_sizes", []),
                "job_titles": priorities.get("job_titles", []),
                "custom_criteria": extracted.get("custom_criteria", []),
                "value_indicators": extracted.get("value_indicators", [])
            }
        except Exception as e:
            logger.error(f"[CATEGORIZATION] Error getting user preferences: {e}")
            return {
                "use_case": "networking",
                "intent": "",
                "goals": "",
                "industries": [],
                "company_sizes": [],
                "job_titles": [],
                "custom_criteria": [],
                "value_indicators": []
            }
    
    def _ai_categorize(self, person, meeting, conversation_text, summary, user_prefs):
        """Use AI to categorize contact based on conversation, profile, and user preferences"""
        try:
            # Prepare data for prompt
            name = person.get("name", "Unknown")
            company = person.get("company", "Unknown")
            job_title = person.get("job_title", "Unknown")
            
            # Format lists for prompt
            industries_str = ", ".join(user_prefs.get("industries", [])) or "Not specified"
            company_sizes_str = ", ".join(user_prefs.get("company_sizes", [])) or "Not specified"
            job_titles_str = ", ".join(user_prefs.get("job_titles", [])) or "Not specified"
            custom_criteria_str = ", ".join(user_prefs.get("custom_criteria", [])) or "None"
            value_indicators_str = ", ".join(user_prefs.get("value_indicators", [])) or "None"
            
            # Format prompt with few-shot examples
            user_prompt = format_prompt(
                self.prompt_config["user_prompt_template"],
                few_shot_examples=self.prompt_config["few_shot_examples"],
                use_case=user_prefs.get("use_case", "networking"),
                user_intent=user_prefs.get("intent", ""),
                user_goals=user_prefs.get("goals", ""),
                industries=industries_str,
                company_sizes=company_sizes_str,
                job_titles=job_titles_str,
                custom_criteria=custom_criteria_str,
                value_indicators=value_indicators_str,
                name=name,
                company=company,
                job_title=job_title,
                summary=summary or "No summary available",
                conversation_text=conversation_text[:2000] if conversation_text else "No conversation text available"  # Limit length
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.prompt_config["model"],
                messages=[
                    {"role": "system", "content": self.prompt_config["system_message"]},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.prompt_config["temperature"],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            # Validate and normalize result
            priority_group = result.get("priority_group", "P2")
            if priority_group not in ["P0", "P1", "P2"]:
                priority_group = "P2"
            
            score = float(result.get("score", 0.5))
            score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
            
            return {
                "priority_group": priority_group,
                "score": score,
                "reasons": result.get("reasons", []),
                "persona": result.get("persona", ""),
                "urgency_level": result.get("urgency_level", ""),
                "intent_match_score": float(result.get("intent_match_score", 0.0))
            }
        
        except Exception as e:
            logger.error(f"[CATEGORIZATION] Error in AI categorization: {e}", exc_info=True)
            # Fallback to simple categorization
            return self._simple_categorize(person, meeting)
    
    def _simple_categorize(self, person, meeting):
        """Simple fallback categorization"""
        score = 0.5  # Base score
        
        # Boost score if we have more information
        if person.get("name") and person["name"] != "Unknown":
            score += 0.1
        if person.get("company") and person["company"] != "Unknown":
            score += 0.1
        if person.get("job_title") and person["job_title"] != "Unknown":
            score += 0.1
        
        # Assign priority group
        if score >= 0.7:
            priority_group = "P0"
        elif score >= 0.4:
            priority_group = "P1"
        else:
            priority_group = "P2"
        
        return {
            "priority_group": priority_group,
            "score": score,
            "reasons": [f"Fallback score: {score:.2f}"],
            "persona": "",
            "urgency_level": "",
            "intent_match_score": 0.0
        }
