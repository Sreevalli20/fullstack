"""
Structured Logging utility for FastAPI application.
Logs include timestamps, log level, logger name, and optional request IDs.
"""

import logging
import sys
from app.config import settings

logger = logging.getLogger("weather_backend")
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logger.setLevel(log_level)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

