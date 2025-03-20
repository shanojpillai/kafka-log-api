from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
import enum

class LogLevel(str, enum.Enum):
    """Enumeration of standard log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    WARNING = "WARNING"  # Alternative form
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"

class LogEntry(BaseModel):
    """Model for validating log entries."""
    service: str = Field(..., description="Name of the service generating the log")
    level: LogLevel = Field(..., description="Log level (INFO, WARN, ERROR, etc.)")
    message: str = Field(..., description="Log message content")
    timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="ISO-formatted timestamp"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional contextual information"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "service": "payment-service",
                "level": "ERROR",
                "message": "Payment processing failed: timeout",
                "timestamp": "2023-05-04T12:34:56.789Z",
                "metadata": {
                    "transaction_id": "tx_12345",
                    "user_id": "user_6789",
                    "amount": 99.99
                }
            }
        }

class BatchLogRequest(BaseModel):
    """Model for sending multiple logs in a batch."""
    start_index: int = Field(..., description="Starting index in the Kaggle dataset")
    count: int = Field(10, description="Number of logs to send", ge=1, le=100)
    
    class Config:
        schema_extra = {
            "example": {
                "start_index": 0,
                "count": 10
            }
        }