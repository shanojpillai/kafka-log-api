import json
import logging
from datetime import datetime
import time
import random
import os
import ast  # For safely evaluating string representations of dictionaries

# Create a simple logger for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaLogger:
    def __init__(self):
        """Initialize a mock Kafka producer for development."""
        self.topic = "logs"
        logger.info(f"Mock Kafka producer initialized (development mode)")
        
        # Create a simple in-memory store for logs
        self.logs = []
        
        # Try to load web logs dataset, fall back to mock data if not available
        try:
            if os.path.exists('data/processed_web_logs.csv'):
                import pandas as pd
                df = pd.read_csv('data/processed_web_logs.csv')
                
                # Convert string representation of metadata to actual dictionaries
                df['metadata'] = df['metadata'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
                
                self.kaggle_data = df.to_dict('records')
                logger.info(f"Loaded {len(self.kaggle_data)} logs from Web Logs dataset")
            else:
                self.kaggle_data = self._create_mock_data()
                logger.info(f"Created mock web logs dataset with {len(self.kaggle_data)} entries")
        except Exception as e:
            logger.error(f"Error loading web logs data: {e}")
            self.kaggle_data = self._create_mock_data()
            logger.info(f"Falling back to mock dataset with {len(self.kaggle_data)} entries")
    
    def _create_mock_data(self):
        """Create some mock web log data for development."""
        return [
            {
                "timestamp": "17/May/2015:11:05:51 +0000",
                "service": "web-server",
                "level": "INFO",
                "message": "Request successful for /index.html",
                "metadata": {
                    "ip": "192.168.1.1",
                    "method": "GET",
                    "protocol": "HTTP/1.1",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/58.0.3029.110",
                    "referrer": "-",
                    "size_bytes": 1280
                }
            },
            {
                "timestamp": "17/May/2015:11:06:15 +0000", 
                "service": "web-server",
                "level": "ERROR",
                "message": "Resource not found for /missing-page.html",
                "metadata": {
                    "ip": "192.168.1.5",
                    "method": "GET",
                    "protocol": "HTTP/1.1",
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 8_1_3)",
                    "referrer": "http://example.com/index.html",
                    "size_bytes": 520
                }
            },
            {
                "timestamp": "17/May/2015:11:07:03 +0000",
                "service": "web-server",
                "level": "WARN",
                "message": "Unauthorized for /admin/dashboard",
                "metadata": {
                    "ip": "192.168.1.10",
                    "method": "POST",
                    "protocol": "HTTP/1.1",
                    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) Firefox/37.0",
                    "referrer": "http://example.com/login",
                    "size_bytes": 320
                }
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
            
        # Add Kafka metadata
        log_data["_kafka_offset"] = len(self.logs)
        log_data["_kafka_timestamp"] = int(time.time() * 1000)  # Milliseconds
        log_data["_kafka_topic"] = self.topic
        log_data["_kafka_partition"] = 0
        
        # Simulate network delay
        delay = random.uniform(0.01, 0.1)  # 10-100ms delay
        time.sleep(delay)
        
        # Log and store
        logger.info(f"Mock log sent: {json.dumps(str(log_data)[:100])}...")
        self.logs.append(log_data)
        return {"status": "success", "message": "Log sent (development mode)"}
    
    def send_kaggle_log(self, index):
        """
        Send a log from the web logs dataset.
        
        Args:
            index (int): Index of the log entry to send
            
        Returns:
            dict: Status of the operation
        """
        if index >= len(self.kaggle_data):
            return {"status": "error", "message": f"Index out of range (0-{len(self.kaggle_data)-1})"}
            
        log_data = self.kaggle_data[index].copy()  # Make a copy to avoid modifying the original
        return self.send_log(log_data)
    
    def send_batch_logs(self, start_index, count=10):
        """
        Send multiple logs in sequence from the web logs dataset.
        
        Args:
            start_index (int): Starting index
            count (int): Number of logs to send
            
        Returns:
            dict: Status with count of successfully sent logs
        """
        max_index = len(self.kaggle_data) - 1
        end_index = min(start_index + count, max_index + 1)
        
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