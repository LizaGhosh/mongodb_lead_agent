"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import meetings, groups, admin
import logging
import os
from datetime import datetime

# Configure logging - in serverless (Vercel) or Railway, only log to console
# File logging is disabled for cloud environments
if os.getenv('VERCEL') or os.getenv('RAILWAY_ENVIRONMENT'):
    # Cloud environment - only console logging
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

# Add middleware to log requests and handle errors (only in Vercel)
if os.getenv('VERCEL'):
    from fastapi import Request
    from fastapi.responses import JSONResponse
    import logging
    logger = logging.getLogger(__name__)
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"[VERCEL] Request: {request.method} {request.url.path}")
        logger.info(f"[VERCEL] Query params: {dict(request.query_params)}")
        try:
            response = await call_next(request)
            logger.info(f"[VERCEL] Response status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"[VERCEL] Error processing request: {str(e)}", exc_info=True)
            # Check if it's a MongoDB connection error
            if "MongoDB" in str(e) or "Connection" in str(e) or "pymongo" in str(e).lower():
                return JSONResponse(
                    status_code=503,
                    content={"error": "Database connection failed", "detail": "MongoDB connection error. Please check network access settings."}
                )
            raise

# Include routers
# On Vercel, the /api prefix is already handled by routing, so we use it for both local and Vercel
# The routes will work as /api/meetings in both environments
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
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/health/db")
def health_db():
    """Health check endpoint with MongoDB connection test"""
    try:
        from database.connection import get_database
        db = get_database()
        # Test MongoDB connection
        db.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "mongodb": "accessible"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "message": "MongoDB connection failed. Check network access settings in MongoDB Atlas."
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
