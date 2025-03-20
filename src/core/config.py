import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.config = {
            "kafka.bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            "kafka.topic_name": os.getenv("KAFKA_TOPIC", "logs"),
            "kafka.request_timeout_ms": int(os.getenv("KAFKA_REQUEST_TIMEOUT_MS", "30000")),
            "kafka.retries": int(os.getenv("KAFKA_RETRIES", "3")),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "kaggle.dataset_path": os.getenv("KAGGLE_DATASET_PATH", "data/kaggle_logs.csv"),
        }
    
    def get(self, key, default=None):
        return self.config.get(key, default)

config = Config()