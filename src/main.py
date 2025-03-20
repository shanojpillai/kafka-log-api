from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .api.routes import router

# Setup simple logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Log Streaming API",
    description="A robust API for sending logs to Kafka using Kaggle datasets",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Log Streaming API in development mode")
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Log Streaming API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)