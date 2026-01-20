import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logger
logger = logging.getLogger("proctoring")
logger.setLevel(logging.DEBUG)

# File handler
log_file = os.path.join(LOGS_DIR, f"proctoring_{datetime.now().strftime('%Y%m%d')}.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def log(message, level="INFO"):
    """Log a message with the specified level"""
    if level == "DEBUG":
        logger.debug(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    else:  # INFO
        logger.info(message)
