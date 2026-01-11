"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import meetings, groups, admin
import logging
import os
from datetime import datetime

# Configure logging - in serverless (Vercel), only log to console
# File logging is disabled for serverless environments
if os.getenv('VERCEL'):
    # Serverless environment - only console logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler()]
    )
else:
    # Local development - file and console logging
    os.makedirs('logs', exist_ok=True)
    log_filename = f"logs/backend_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )

app = FastAPI(title="Networking Assistant API")

# CORS middleware
# Get allowed origins from environment variable or allow all for development
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(meetings.router, prefix="/api", tags=["meetings"])
app.include_router(groups.router, prefix="/api", tags=["groups"])
app.include_router(admin.router, prefix="/api", tags=["admin"])

# Import onboarding router
from api.routes import onboarding
app.include_router(onboarding.router, prefix="/api", tags=["onboarding"])

@app.get("/")
def root():
    return {"message": "Networking Assistant API"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
