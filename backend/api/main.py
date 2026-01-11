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
# allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
# if allowed_origins_env:
#     allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]
# else:
#     allowed_origins = ["*"]

# # When using "*" with allow_credentials=True, CORS spec doesn't allow it
# # For mobile browsers, we need to be more explicit
# # If "*" is used, we'll set allow_credentials=False to avoid CORS issues
# use_credentials = "*" not in allowed_origins

allowed_origins_env = os.getenv("ALLOWED_ORIGINS")

if allowed_origins_env:
    allowed_origins = [o.strip().rstrip("/") for o in allowed_origins_env.split(",")]
else:
    # Default to localhost for local development
    allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=allowed_origins,
#     allow_credentials=use_credentials,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Add middleware to log requests and handle errors (only in Vercel)
if os.getenv('VERCEL'):
    from fastapi import Request
    from fastapi.responses import JSONResponse
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        # Log request details - these will appear in Vercel logs
        print(f"[VERCEL LOG] ========== REQUEST START ==========")
        print(f"[VERCEL LOG] Method: {request.method}")
        print(f"[VERCEL LOG] Path: {request.url.path}")
        print(f"[VERCEL LOG] Query: {dict(request.query_params)}")
        print(f"[VERCEL LOG] Headers: {dict(request.headers)}")
        
        logger.info(f"[VERCEL] Request: {request.method} {request.url.path}")
        logger.info(f"[VERCEL] Query params: {dict(request.query_params)}")
        
        try:
            response = await call_next(request)
            print(f"[VERCEL LOG] Response Status: {response.status_code}")
            print(f"[VERCEL LOG] ========== REQUEST END ==========")
            logger.info(f"[VERCEL] Response status: {response.status_code}")
            return response
        except Exception as e:
            # Print full error details - these will show in Vercel logs
            print(f"[VERCEL LOG] ========== ERROR OCCURRED ==========")
            print(f"[VERCEL LOG] Error Type: {type(e).__name__}")
            print(f"[VERCEL LOG] Error Message: {str(e)}")
            print(f"[VERCEL LOG] Traceback:")
            print(traceback.format_exc())
            print(f"[VERCEL LOG] =====================================")
            
            logger.error(f"[VERCEL] Error processing request: {str(e)}", exc_info=True)
            # Check if it's a MongoDB connection error
            if "MongoDB" in str(e) or "Connection" in str(e) or "pymongo" in str(e).lower():
                return JSONResponse(
                    status_code=503,
                    content={"error": "Database connection failed", "detail": "MongoDB connection error. Please check network access settings."}
                )
            raise

# Include routers
# On Vercel, the /api prefix is preserved in the path when it reaches FastAPI
# So we keep the /api prefix for both local and Vercel environments
# Vercel routes /api/* to the serverless function, and Mangum preserves the full path
# So a request to /api/onboarding in Vercel matches /api/onboarding route in FastAPI
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
    # Force print to test logging
    print("=" * 80)
    print("[HEALTH CHECK] Testing MongoDB connection...")
    print(f"[HEALTH CHECK] Timestamp: {datetime.now().isoformat()}")
    
    try:
        from database.connection import get_database
        db = get_database()
        # Test MongoDB connection
        db.admin.command('ping')
        print("[HEALTH CHECK] ✅ MongoDB connection successful")
        print("=" * 80)
        return {
            "status": "healthy",
            "database": "connected",
            "mongodb": "accessible"
        }
    except Exception as e:
        print(f"[HEALTH CHECK] ❌ MongoDB connection failed: {str(e)}")
        print("=" * 80)
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "message": "MongoDB connection failed. Check network access settings in MongoDB Atlas."
        }

@app.get("/api/test-logs")
def test_logs():
    """Test endpoint to verify logging is working in Vercel"""
    import sys
    print("=" * 80)
    print("[TEST LOGS] This is a test log message")
    print(f"[TEST LOGS] Python version: {sys.version}")
    print(f"[TEST LOGS] Timestamp: {datetime.now().isoformat()}")
    print("[TEST LOGS] If you see this in Vercel logs, logging is working!")
    print("=" * 80)
    
    # Also use logger
    logger = logging.getLogger(__name__)
    logger.info("[TEST LOGS] Logger test message")
    
    return {
        "message": "Check Vercel logs for test messages",
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
