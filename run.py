import os
import uvicorn
import logging

def main():
    # GCP Cloud Run uses PORT environment variable (default 8080)
    port = int(os.environ.get("PORT", 8080))
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print(f"🚀 Starting RAG System API on 0.0.0.0:{port}")
    print(f"☁️ Running on Google Cloud Platform - Cloud Run")
    print(f"🌍 Environment: {os.environ.get('ENVIRONMENT', 'production')}")
    
    # Import app here to avoid circular imports and early initialization
    try:
        from app.main import app
        print("✅ Application imported successfully")
    except Exception as e:
        print(f"❌ Failed to import application: {e}")
        raise
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
        access_log=True,
        timeout_keep_alive=300,
        # Cloud Run specific optimizations
        workers=1,  # Cloud Run manages scaling
        loop="asyncio",
        http="httptools"
    )

if __name__ == "__main__":
    main()