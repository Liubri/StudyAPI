import logging
import sys

# Configure logging format
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)

# Configure root logger
def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Add console handler
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for different modules
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return root_logger

# Create logger instance
logger = setup_logging() 