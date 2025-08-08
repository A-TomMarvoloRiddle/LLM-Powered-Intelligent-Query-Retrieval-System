import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on 0.0.0.0:{port}")
    uvicorn.run(
        app,  # Pass the app object directly, not as string
        host="0.0.0.0",
        port=port,
        reload=False,  # Don't use reload in production
        log_level="info",
        access_log=True,  # Enable access logs
    )