"""Application settings and configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "networking_assistant"

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Google Custom Search API Configuration (not currently used - research agent removed)
# Free tier: 100 queries/day
# Get API key: https://developers.google.com/custom-search/v1/overview
# Create CSE: https://programmablesearchengine.google.com/controlpanel/create
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")  # Custom Search Engine ID

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
