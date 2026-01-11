"""
Vercel serverless function entry point for FastAPI
This file is required for Vercel to properly route API requests
"""
import sys
import os

# Get the project root directory (parent of api/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, 'backend')

# Add backend directory to Python path
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import the FastAPI app from backend
from api.main import app

# Export the app for Vercel
# Vercel's @vercel/python runtime will handle the ASGI app
handler = app
