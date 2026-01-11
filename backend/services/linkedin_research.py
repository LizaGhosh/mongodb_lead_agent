"""LinkedIn research service for enriching person profiles"""
from config.settings import OPENAI_API_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID
from openai import OpenAI
import logging
import json
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

def search_google_for_linkedin(name, company, job_title=None):
    """
    Search Google for LinkedIn profile URL using Google Custom Search API
    
    Free tier: 100 queries/day
    
    Args:
        name: Person's name
        company: Company name
        job_title: Job title (optional)
        
    Returns:
        str: LinkedIn profile URL or None
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        logger.warning("[LINKEDIN] Google API credentials not set. Skipping Google search.")
        return None
    
    try:
        from googleapiclient.discovery import build
        
        # Build search query
        search_query = f'"{name}" "{company}" site:linkedin.com/in'
        if job_title:
            search_query += f' "{job_title}"'
        
        logger.info(f"[LINKEDIN] Google search query: {search_query}")
        
        # Build Google Custom Search service
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        
        # Execute search
        result = service.cse().list(
            q=search_query,
            cx=GOOGLE_CSE_ID,
            num=1  # Only need first result
        ).execute()
        
        # Extract LinkedIn URL from results
        if 'items' in result and len(result['items']) > 0:
            linkedin_url = result['items'][0]['link']
            logger.info(f"[LINKEDIN] Found LinkedIn URL: {linkedin_url}")
            return linkedin_url
        else:
            logger.info(f"[LINKEDIN] No LinkedIn profile found in Google search")
            return None
    
    except ImportError:
        logger.warning("[LINKEDIN] google-api-python-client not installed. Install with: pip install google-api-python-client")
        return None
    except Exception as e:
        logger.error(f"[LINKEDIN] Error in Google search: {e}", exc_info=True)
        return None

def scrape_public_linkedin_data(linkedin_url):
    """
    Scrape public LinkedIn profile data (headline, location, etc.)
    
    Note: Only works for public profiles. May violate LinkedIn ToS.
    For hackathon/demo purposes only.
    
    Args:
        linkedin_url: LinkedIn profile URL
        
    Returns:
        dict: Scraped profile data
    """
    if not linkedin_url:
        return None
    
    try:
        # Use a simple HTTP request to get public profile
        # Note: LinkedIn requires authentication for most data
        # This will only work for completely public profiles
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(linkedin_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info from meta tags or page content
            # Note: LinkedIn's HTML structure changes frequently
            profile_data = {
                "linkedin_url": linkedin_url,
                "headline": None,
                "location": None,
                "summary": None
            }
            
            # Try to extract from meta tags
            title_tag = soup.find('title')
            if title_tag:
                profile_data["headline"] = title_tag.get_text().strip()
            
            # Try to find location in meta tags
            location_meta = soup.find('meta', {'property': 'og:description'})
            if location_meta:
                profile_data["summary"] = location_meta.get('content', '').strip()
            
            logger.info(f"[LINKEDIN] Scraped basic data from {linkedin_url}")
            return profile_data
        else:
            logger.warning(f"[LINKEDIN] Could not access LinkedIn profile: {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"[LINKEDIN] Error scraping LinkedIn: {e}", exc_info=True)
        return None

def search_linkedin_profile(name, company, job_title=None):
    """
    Search for LinkedIn profile information using free resources
    
    Strategy:
    1. Try Google Custom Search API (free: 100 queries/day) to find LinkedIn URL
    2. If URL found, try to scrape public data
    3. Fallback to AI-generated data if search/scraping fails
    
    Args:
        name: Person's name
        company: Company name
        job_title: Job title (optional)
        
    Returns:
        dict: LinkedIn profile data
    """
    if not name or name == "Unknown" or not company or company == "Unknown":
        logger.warning("[LINKEDIN] Insufficient data for LinkedIn search")
        return None
    
    # Strategy 1: Try Google Custom Search to find LinkedIn URL
    linkedin_url = search_google_for_linkedin(name, company, job_title)
    
    profile_data = None
    
    # Strategy 2: If URL found, try to scrape public data
    if linkedin_url:
        profile_data = scrape_public_linkedin_data(linkedin_url)
    
    # Strategy 3: Fallback to AI-generated data
    if not profile_data and OPENAI_API_KEY:
        logger.info(f"[LINKEDIN] Falling back to AI-generated profile data")
        profile_data = generate_ai_linkedin_profile(name, company, job_title, linkedin_url)
    
    return profile_data

def generate_ai_linkedin_profile(name, company, job_title=None, linkedin_url=None):
    """Generate realistic LinkedIn profile using AI (fallback method)"""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        logger.info(f"[LINKEDIN] Generating AI profile for: {name} at {company}")
        
        prompt = f"""Based on the following information, generate a realistic LinkedIn profile summary:
        
Name: {name}
Company: {company}
Job Title: {job_title or "Not specified"}
LinkedIn URL: {linkedin_url or "Not found"}

Generate a JSON object with the following structure:
{{
  "linkedin_url": "{linkedin_url or 'https://www.linkedin.com/in/[username]'}",
  "headline": "Professional headline (e.g., 'CTO at TechCorp | AI & Cloud Expert')",
  "experience": [
    {{
      "title": "Current or most recent job title",
      "company": "Company name",
      "duration": "Time period",
      "description": "Brief description"
    }}
  ],
  "education": [
    {{
      "school": "University name",
      "degree": "Degree type",
      "field": "Field of study"
    }}
  ],
  "skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "connections": "500+",
  "summary": "2-3 sentence professional summary",
  "location": "City, Country"
}}

Return only valid JSON."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a LinkedIn profile data generator. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON
        try:
            profile_data = json.loads(result_text)
            profile_data["research_source"] = "ai_generated" if not linkedin_url else "google_search_ai_enriched"
            logger.info(f"[LINKEDIN] Successfully generated profile data for {name}")
            return profile_data
        except json.JSONDecodeError as e:
            logger.error(f"[LINKEDIN] Error parsing JSON: {e}")
            return None
    
    except Exception as e:
        logger.error(f"[LINKEDIN] Error generating AI profile: {e}", exc_info=True)
        return None
