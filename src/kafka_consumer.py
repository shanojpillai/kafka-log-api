import json
import threading
import time
import logging
from datetime import datetime
from queue import Queue
from .kafka_producer import kafka_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaConsumer:
    def __init__(self):
        """Initialize a mock Kafka consumer for development."""
        self.topic = kafka_logger.topic
        self.is_running = False
        self.consumers = []
        self.lock = threading.Lock()  # Lock for thread-safe access to logs
        self.consumer_thread = None
        logger.info("Mock Kafka consumer initialized (development mode)")
        
        # Connect to the producer's log store
        self.logs = kafka_logger.logs

    def register_consumer(self, callback):
        """Register a callback function to receive messages."""
        with self.lock:
            self.consumers.append(callback)
        logger.info(f"New consumer registered. Total consumers: {len(self.consumers)}")
        return len(self.consumers) - 1

    def start(self):
        """Start consuming messages."""
        if self.is_running:
            logger.warning("Consumer is already running")
            return
        
        self.is_running = True
        self.consumer_thread = threading.Thread(target=self._consume_loop, daemon=True)
        self.consumer_thread.start()
        logger.info("Consumer started")

    def stop(self):
        """Stop consuming messages."""
        if not self.is_running:
            logger.warning("Consumer is not running")
            return
        
        self.is_running = False
        if self.consumer_thread:
            self.consumer_thread.join(timeout=1.0)
            self.consumer_thread = None
        logger.info("Consumer stopped")

    def _consume_loop(self):
        """Main loop for consuming messages."""
        last_log_count = 0

        while self.is_running:
            with self.lock:
                current_log_count = len(self.logs)

                # Check if new logs have been added
                if current_log_count > last_log_count:
                    new_logs = self.logs[last_log_count:current_log_count]
                    for log_entry in new_logs:
                        self._process_message(log_entry)
                    last_log_count = current_log_count

            # Sleep to reduce CPU usage
            time.sleep(0.1)

    def _process_message(self, message):
        """Process a message and send it to all registered consumers."""
        logger.debug(f"Processing message: {message}")
        
        # Add reception timestamp
        message['_received_at'] = datetime.now().isoformat()
        
        # Notify all consumers
        for consumer in self.consumers:
            try:
                consumer(message)
            except Exception as e:
                logger.error(f"Error in consumer callback: {e}")
                logger.debug(f"Faulty message: {message}")
        
        logger.info(f"Processed message from service: {message.get('service', 'UNKNOWN')}, level: {message.get('level', 'UNKNOWN')}")

# Create a singleton instance
kafka_consumer = KafkaConsumer()