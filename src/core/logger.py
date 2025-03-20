import logging

def setup_logger(name):
    """Set up and return a logger instance with standardized configuration."""
    logger = logging.getLogger(name)
    
    # Set log level
    logger.setLevel(logging.INFO)
    
    # Create console handler if not already added
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger