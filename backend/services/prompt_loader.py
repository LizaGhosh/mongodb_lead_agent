"""Prompt loader utility for loading prompts from YAML files"""
import yaml
import os
from pathlib import Path

# Get the prompts directory path
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def load_prompt(prompt_file):
    """
    Load a prompt configuration from a YAML file
    
    Args:
        prompt_file: Name of the YAML file (e.g., "extraction.yaml")
        
    Returns:
        dict: Prompt configuration with all fields from YAML
    """
    prompt_path = PROMPTS_DIR / prompt_file
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_config = yaml.safe_load(f)
    
    return prompt_config

def format_prompt(template, **kwargs):
    """
    Format a prompt template with provided variables
    
    Args:
        template: Prompt template string with {placeholders}
        **kwargs: Variables to fill in the template
        
    Returns:
        str: Formatted prompt string
    """
    return template.format(**kwargs)
