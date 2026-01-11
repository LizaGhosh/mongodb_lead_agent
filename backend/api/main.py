"""FastAPI application entry point"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import meetings, groups



def setup_logging():
    # Default: console logging (works everywhere, best for Vercel)
    handlers = [logging.StreamHandler()]

    # If NOT running on Vercel, also log to a local file
    # Vercel sets VERCEL=1 (and/or VERCEL_ENV)
    is_vercel = os.getenv("VERCEL") == "1" or bool(os.getenv("VERCEL_ENV"))
    if not is_vercel:
        os.makedirs("logs", exist_ok=True)
        log_filename = f"logs/backend_{datetime.now().strftime('%Y%m%d')}.log"
        handlers.insert(0, logging.FileHandler(log_filename, encoding="utf-8"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,  # important in serverless to avoid duplicate/ignored config
    )

setup_logging()

app = FastAPI(title="Networking Assistant API")



# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from api.routes import meetings, groups
# import logging

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )

# app = FastAPI(title="Networking Assistant API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(meetings.router, prefix="/api", tags=["meetings"])
app.include_router(groups.router, prefix="/api", tags=["groups"])

@app.get("/")
def root():
    return {"message": "Networking Assistant API"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
