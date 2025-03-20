from fastapi import APIRouter, HTTPException
from src.api.models import LogEntry, BatchLogRequest
from src.core.kafka_producer import kafka_logger
from src.core.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

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