import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app first
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

# Basic health check endpoint
@app.get("/")
async def root():
    return {
        "message": "RAG System API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Try to import routes, but don't fail if they don't exist
try:
    from app.api.routes import router
    app.include_router(router)
    print("✓ API routes loaded successfully")
except ImportError as e:
    print(f"⚠️ Could not load API routes: {e}")
    print("Running with basic endpoints only")

# Try to import settings, but use defaults if not available
try:
    from app.config.settings import settings
    environment = settings.environment
except ImportError:
    print("⚠️ Could not load settings, using defaults")
    environment = "development"

# Try to import logger, but use print if not available
try:
    from app.utils.logger import logger
    log_func = logger.info
except ImportError:
    print("⚠️ Could not load logger, using print")
    log_func = print

@app.on_event("startup")
async def startup_event():
    log_func("Starting RAG System API...")
    log_func(f"Environment: {environment}")
    port = os.environ.get("PORT", "8000")
    log_func(f"Server will run on port: {port}")

@app.on_event("shutdown")
async def shutdown_event():
    log_func("Shutting down RAG System API...")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Running directly - starting on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)