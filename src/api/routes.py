from fastapi import APIRouter, HTTPException
from .models import LogEntry, BatchLogRequest
from ..core.kafka_producer import kafka_logger
import logging

# Setup simple logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/log")
async def create_log(log_entry: LogEntry):
    """
    Submit a new log entry to the logging system.
    
    The log entry will be validated and sent to Kafka for processing.
    """
    logger.debug(f"Received log entry: {log_entry.dict()}")
    
    response = kafka_logger.send_log(log_entry.dict())
    
    if response["status"] == "error":
        logger.error(f"Failed to send log: {response['message']}")
        raise HTTPException(status_code=500, detail=response["message"])
        
    return {"status": "success", "message": "Log entry accepted"}

@router.get("/kaggle/{index}")
async def send_kaggle_log(index: int):
    """
    Send a log entry from the Kaggle dataset.
    
    Args:
        index: Index in the Kaggle dataset
    """
    logger.info(f"Sending Kaggle log at index {index}")
    response = kafka_logger.send_kaggle_log(index)
    
    if response["status"] == "error":
        raise HTTPException(status_code=404, detail=response["message"])
        
    return {"status": "success", "message": f"Kaggle log at index {index} sent"}

@router.post("/kaggle/batch")
async def send_batch_logs(request: BatchLogRequest):
    """
    Send multiple logs from the Kaggle dataset.
    
    Args:
        request: Batch request parameters
    """
    logger.info(f"Sending batch of {request.count} Kaggle logs starting at index {request.start_index}")
    response = kafka_logger.send_batch_logs(request.start_index, request.count)
    
    if response["status"] == "error":
        raise HTTPException(status_code=500, detail=response["message"])
        
    return {
        "status": "success", 
        "message": f"Sent {response['success_count']} logs",
        "success_count": response["success_count"]
    }

@router.get("/logs")
async def get_logs(limit: int = 10, service: str = None, level: str = None):
    """
    Retrieve logs from the in-memory store.
    
    Args:
        limit: Maximum number of logs to return
        service: Filter by service name
        level: Filter by log level
    """
    logs = kafka_logger.logs.copy()
    
    # Apply filters
    if service:
        logs = [log for log in logs if log.get("service") == service]
    if level:
        logs = [log for log in logs if log.get("level") == level]
    
    # Get the most recent logs
    logs = logs[:limit]
    
    return {
        "status": "success",
        "count": len(logs),
        "logs": logs
    }

@router.get("/health")
async def health_check():
    """
    Check the health of the logging service.
    """
    return {"status": "healthy", "mode": "development"}

@router.get("/dataset/info")
async def get_dataset_info():
    """Get information about the loaded Kaggle dataset."""
    return {
        "status": "success",
        "total_logs": len(kafka_logger.kaggle_data),
        "sample": kafka_logger.kaggle_data[:3]
    }