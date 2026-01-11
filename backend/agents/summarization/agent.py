"""Summarization Agent - Creates conversation summaries"""
from agents.base_agent import BaseAgent
from services.agent_registry import register_agent
from services.prompt_loader import load_prompt, format_prompt
from config.settings import OPENAI_API_KEY
from openai import OpenAI
from datetime import datetime

class SummarizationAgent(BaseAgent):
    """Creates concise summaries of conversations"""
    
    def __init__(self):
        super().__init__(
            agent_id="summarization_agent",
            agent_type="summarization",
            skills=["text_summarization", "conversation_analysis"],
            capabilities={
                "input_types": ["text", "conversation"],
                "output_types": ["summary", "key_points"]
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
        self.prompt_config = load_prompt("summarization.yaml")
    
    def _get_summary_context(self, user_id="default"):
        """Get summary context from user preferences"""
        try:
            user_prefs = self.db.user_preferences.find_one({"user_id": user_id})
            
            if not user_prefs:
                # Default context if no preferences found
                return {
                    "use_case": "networking",
                    "focus_areas": ["key discussion points", "mutual interests", "commitments"],
                    "extracted_preferences": {}
                }
            
            # Build context from user preferences
            context = {
                "use_case": user_prefs.get("use_case", "networking"),
                "focus_areas": []
            }
            
            # Add use-case specific focus areas
            use_case = user_prefs.get("use_case", "networking")
            if use_case == "sales":
                context["focus_areas"] = ["budget discussions", "pain points", "decision timeline", "buying signals"]
            elif use_case == "job_hunting":
                context["focus_areas"] = ["hiring needs", "role details", "team structure", "interview process"]
            elif use_case == "lead_generation":
                context["focus_areas"] = ["company needs", "decision makers", "buying signals", "company size"]
            else:
                context["focus_areas"] = ["key discussion points", "mutual interests", "commitments"]
            
            # Add extracted preferences from comments
            extracted = user_prefs.get("extracted_preferences", {})
            context["extracted_preferences"] = extracted
            
            # Add custom criteria to focus on
            if extracted.get("custom_criteria"):
                context["focus_areas"].extend([f"mentions of: {crit}" for crit in extracted["custom_criteria"][:3]])
            
            return context
        
        except Exception as e:
            print(f"Error getting user preferences: {e}")
            # Return default context
            return {
                "use_case": "networking",
                "focus_areas": ["key discussion points", "mutual interests", "commitments"],
                "extracted_preferences": {}
            }
    
    def summarize(self, text, meeting_id, user_id="default"):
        """Create summary of conversation with context from user preferences"""
        self.update_status("busy")
        
        try:
            if not self.client:
                # Fallback: simple summary
                return self._simple_summarize(text, meeting_id)
            
            # Get person information for context
            meeting = self.db.meetings.find_one({"meeting_id": meeting_id})
            person = None
            if meeting:
                person = self.db.people.find_one({"person_id": meeting.get("person_id")})
            
            # Get summary context from user preferences
            context = self._get_summary_context(user_id)
            
            # Build context-aware prompt
            focus_areas_str = ", ".join(context["focus_areas"])
            use_case_note = f"User's goal: {context['use_case']}. " if context.get("use_case") else ""
            
            # Add extracted preferences if available
            extracted_note = ""
            if context.get("extracted_preferences", {}).get("value_indicators"):
                indicators = context["extracted_preferences"]["value_indicators"][:2]
                extracted_note = f"Pay special attention to: {', '.join(indicators)}. "
            
            # Include person name and company in summary if available
            person_info = ""
            if person:
                name = person.get("name", "").strip()
                company = person.get("company", "").strip()
                if name and name != "Unknown":
                    person_info = f"Person: {name}. "
                if company and company != "Unknown":
                    person_info += f"Company: {company}. "
            
            # Load prompt from YAML and format it
            user_prompt = format_prompt(
                self.prompt_config["user_prompt_template"],
                person_info=person_info,
                use_case_note=use_case_note,
                extracted_note=extracted_note,
                focus_areas_str=focus_areas_str,
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
            
            summary_text = response.choices[0].message.content.strip()
            
            # Update meeting document
            self.db.meetings.update_one(
                {"meeting_id": meeting_id},
                {
                    "$set": {
                        "summary": {
                            "text": summary_text,
                            "key_points": [],
                            "created_at": datetime.now()
                        }
                    }
                }
            )
            
            self.update_status("idle")
            return summary_text
        
        except Exception as e:
            self.update_status("idle")
            return self._simple_summarize(text, meeting_id)
    
    def _simple_summarize(self, text, meeting_id):
        """Simple fallback summary"""
        # Truncate text as simple summary
        summary = text[:200] + "..." if len(text) > 200 else text
        
        self.db.meetings.update_one(
            {"meeting_id": meeting_id},
            {
                "$set": {
                    "summary": {
                        "text": summary,
                        "key_points": [],
                        "created_at": datetime.now()
                    }
                }
            }
        )
        
        return summary
