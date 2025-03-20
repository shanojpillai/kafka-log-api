import json
import logging
from datetime import datetime
from src.core.config import config
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class KafkaLogger:
    def __init__(self):
        """Initialize a mock Kafka producer for development."""
        self.topic = config.get("kafka.topic_name")
        logger.info(f"Mock Kafka producer initialized (development mode)")
        
        # Create a simple in-memory store for logs
        self.logs = []
        
        # Create mock Kaggle data
        self.kaggle_data = self._create_mock_data()
        logger.info(f"Created mock Kaggle dataset with {len(self.kaggle_data)} entries")
    
    def _create_mock_data(self):
        """Create some mock log data for development."""
        return [
            {
                "timestamp": "2023-05-01T10:15:30.123Z",
                "service": "auth-service",
                "level": "INFO",
                "message": "User login successful",
                "metadata": {"user_id": "u123", "ip": "192.168.1.1"}
            },
            {
                "timestamp": "2023-05-01T10:16:45.789Z", 
                "service": "payment-service",
                "level": "ERROR",
                "message": "Payment processing failed",
                "metadata": {"transaction_id": "tx456", "amount": 99.99}
            },
            {
                "timestamp": "2023-05-01T10:17:12.456Z",
                "service": "inventory-service",
                "level": "WARN",
                "message": "Low stock detected",
                "metadata": {"product_id": "p789", "quantity": 5}
            }
        ]

    def send_log(self, log_data):
        """
        Mock sending a log message to Kafka.
        
        Args:
            log_data (dict): Log data to be sent
            
        Returns:
            dict: Status of the operation
        """
        if not isinstance(log_data, dict):
            return {"status": "error", "message": "Log data must be a dictionary"}
        
        # Ensure timestamp exists
        if "timestamp" not in log_data:
            log_data["timestamp"] = datetime.now().isoformat()
            
        logger.info(f"Mock log sent: {json.dumps(log_data)[:100]}...")
        self.logs.append(log_data)
        return {"status": "success", "message": "Log sent (development mode)"}
    
    def send_kaggle_log(self, index):
        """
        Send a log from the mock Kaggle dataset.
        
        Args:
            index (int): Index of the log entry to send
            
        Returns:
            dict: Status of the operation
        """
        if index >= len(self.kaggle_data):
            return {"status": "error", "message": f"Index out of range (0-{len(self.kaggle_data)-1})"}
            
        log_data = self.kaggle_data[index]
        return self.send_log(log_data)
    
    def send_batch_logs(self, start_index, count=10):
        """
        Send multiple logs in sequence from the mock Kaggle dataset.
        
        Args:
            start_index (int): Starting index
            count (int): Number of logs to send
            
        Returns:
            dict: Status with count of successfully sent logs
        """
        max_index = len(self.kaggle_data) - 1
        end_index = min(start_index + count, max_index)
        
        success_count = 0
        for i in range(start_index, end_index):
            result = self.send_kaggle_log(i)
            if result["status"] == "success":
                success_count += 1
                
        return {
            "status": "success" if success_count > 0 else "error",
            "message": f"Successfully sent {success_count}/{count} logs",
            "success_count": success_count
        }

# Create a singleton instance
kafka_logger = KafkaLogger()