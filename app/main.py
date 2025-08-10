import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RAG System API",
    description="Production-ready RAG system for policy document analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Method: {request.method} | "
        f"URL: {request.url} | "
        f"Status: {response.status_code} | "
        f"Process Time: {process_time:.4f}s"
    )
    return response

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "🚀 RAG System API is running on Google Cloud Run",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": time.time(),
        "environment": os.environ.get("ENVIRONMENT", "production"),
        "docs_url": "/docs",
        "api_endpoint": "/hackrx/run"
    }

# Health check endpoint (required for Cloud Run)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "rag-system",
        "platform": "gcp-cloud-run",
        "port": os.environ.get("PORT", "8080")
    }

# Startup status endpoint
@app.get("/status")
async def service_status():
    try:
        # Try to import settings
        from app.config.settings import settings
        environment = settings.environment
        
        return {
            "status": "ready",
            "message": "All services operational",
            "environment": environment,
            "timestamp": time.time(),
            "endpoints": {
                "main_api": "/hackrx/run",
                "health": "/health", 
                "docs": "/docs",
                "queries": "/queries"
            }
        }
    except Exception as e:
        return {
            "status": "partial",
            "message": "Basic endpoints only - Some services may be initializing",
            "error": str(e),
            "timestamp": time.time()
        }

# Initialize services and routes
logger.info("🔧 Initializing RAG System on Cloud Run...")

# Try to load routes with proper error handling
try:
    logger.info("📡 Loading API routes...")
    from app.api.routes import router
    app.include_router(router)
    logger.info("✅ API routes loaded successfully")
    
    # Success endpoint
    @app.get("/ready")
    async def ready_check():
        return {
            "status": "ready",
            "message": "RAG System fully operational",
            "timestamp": time.time(),
            "all_services": "loaded"
        }
        
except Exception as e:
    logger.error(f"⚠️ Could not load API routes: {e}")
    
    # Add fallback endpoints
    @app.get("/ready")
    async def ready_check():
        return {
            "status": "degraded",
            "message": "Basic endpoints only - RAG services may be initializing",
            "error": str(e),
            "timestamp": time.time()
        }
    
    @app.post("/hackrx/run")
    async def fallback_endpoint():
        return JSONResponse(
            status_code=503,
            content={
                "error": "RAG services are initializing",
                "message": "Please try again in a few moments",
                "timestamp": time.time()
            }
        )

# Load environment settings
try:
    from app.config.settings import settings
    environment = settings.environment
    logger.info(f"🌍 Environment: {environment}")
except ImportError as e:
    logger.warning(f"⚠️ Could not load settings: {e}")
    environment = "production"

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    port = os.environ.get("PORT", "8080")
    logger.info("🚀 Starting RAG System API on Google Cloud Run...")
    logger.info(f"🌍 Environment: {environment}")
    logger.info(f"🔌 Server running on port: {port}")
    logger.info(f"📚 API Documentation: https://your-service-url/docs")
    logger.info(f"🔍 Health Check: https://your-service-url/health")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down RAG System API...")

# Exception handlers
@app.exception_handler(500)
async def internal_server_error(request: Request, exc: Exception):
    logger.error(f"Internal Server Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Something went wrong. Please try again later.",
            "timestamp": time.time()
        }
    )

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🔧 Running in development mode on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)