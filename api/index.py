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

# Set Vercel environment variable
os.environ['VERCEL'] = '1'

# Import the FastAPI app from backend
from api.main import app
from mangum import Mangum

# Wrap FastAPI app with Mangum for AWS Lambda/Vercel compatibility
# Mangum converts ASGI to AWS Lambda event format
# Note: Vercel preserves the full path when routing /api/* to this function
# So a request to /api/meetings will have path="/api/meetings" in the event
handler = Mangum(app, lifespan="off")
