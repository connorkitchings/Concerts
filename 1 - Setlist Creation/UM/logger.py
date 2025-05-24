"""
Band-specific logger for UM pipeline.

Wraps the general get_logger utility and loads all settings from UM/config.py.
"""
from logger import get_logger as general_get_logger
from UM.config import LOG_FILE, LOG_LEVEL, LOG_MAX_BYTES, LOG_BACKUP_COUNT

def get_logger(name: str) -> 'logging.Logger':
    """
    Get a UM-configured logger instance.

    Args:
        name (str): Name of the logger (usually __name__).
    Returns:
        logging.Logger: Configured logger instance for UM.
    """
    return general_get_logger(
        name=name,
        log_file=LOG_FILE,
        log_level=LOG_LEVEL,
        log_max_bytes=LOG_MAX_BYTES,
        log_backup_count=LOG_BACKUP_COUNT
    )
