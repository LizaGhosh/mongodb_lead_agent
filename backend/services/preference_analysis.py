"""Preference analysis service for extracting insights from user comments"""
from config.settings import OPENAI_API_KEY
from services.prompt_loader import load_prompt, format_prompt
from openai import OpenAI
import json
import re

def analyze_comments(comments):
    """
    Analyze user comments to extract implicit preferences
    
    Args:
        comments: Free-form text from user
        
    Returns:
        dict: Extracted preferences including custom criteria, value indicators, etc.
    """
    if not comments or not comments.strip():
        return {}
    
    if not OPENAI_API_KEY:
        # Fallback: simple keyword extraction
        return _simple_extract(comments)
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Load prompts from YAML
        prompt_config = load_prompt("preference_analysis.yaml")
        
        # Format prompt with comments
        user_prompt = format_prompt(
            prompt_config["user_prompt_template"],
            comments=comments
        )

        response = client.chat.completions.create(
            model=prompt_config["model"],
            messages=[
                {"role": "system", "content": prompt_config["system_message"]},
                {"role": "user", "content": user_prompt}
            ],
            temperature=prompt_config["temperature"]
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Try to parse JSON
        try:
            # Remove markdown code blocks if present
            result_text = re.sub(r'```json\s*', '', result_text)
            result_text = re.sub(r'```\s*', '', result_text)
            extracted = json.loads(result_text)
            return extracted
        except:
            # If JSON parsing fails, use simple extraction
            return _simple_extract(comments)
    
    except Exception as e:
        print(f"Error analyzing comments: {e}")
        return _simple_extract(comments)

def _simple_extract(comments):
    """Simple fallback extraction using keyword matching"""
    extracted = {
        "additional_industries": [],
        "custom_criteria": [],
        "value_indicators": [],
        "special_requirements": [],
        "exclusion_criteria": []
    }
    
    # Simple keyword extraction (basic implementation)
    text_lower = comments.lower()
    
    # Look for funding mentions
    if any(word in text_lower for word in ['series a', 'series b', 'funding', 'raised']):
        extracted["custom_criteria"].append("Funding stage mentioned")
    
    # Look for remote work mentions
    if any(word in text_lower for word in ['remote', 'remote-first', 'distributed']):
        extracted["custom_criteria"].append("Remote work culture")
    
    return extracted
