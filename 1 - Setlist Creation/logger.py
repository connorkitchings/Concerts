"""
General Logger Utility
=====================

Provides a reusable logger configuration function for all band pipelines. Uses a size-based file handler (RotatingFileHandler) to ensure log files do not grow indefinitely.

Usage:
    from logger import get_logger
    logger = get_logger(
        name=__name__,
        log_file="/path/to/logfile.log",
        log_level="INFO",
        log_max_bytes=5 * 1024 * 1024,
        log_backup_count=5
    )

All arguments are type-hinted and documented. This logger is intended to be wrapped by band-specific logger.py modules for config-driven logging.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional

def get_logger(
    name: str,
    log_file: str = "../../logs/data_pipeline.log",
    log_level: str = 'INFO',
    log_max_bytes: int = 5 * 1024 * 1024,
    log_backup_count: int = 5,
    add_console_handler: bool = True
) -> logging.Logger:
    """
    Create and configure a logger with a size-based rotating file handler.

    Args:
        name (str): Name of the logger (usually __name__).
        log_file (str): Full path to the log file. Parent directories will be created if needed.
        log_level (str, optional): Logging level (e.g., 'INFO', 'DEBUG'). Defaults to 'INFO'.
        log_max_bytes (int, optional): Maximum size in bytes before rotating log. Defaults to 5 MB.
        log_backup_count (int, optional): Number of backup log files to keep. Defaults to 5.
        add_console_handler (bool, optional): If True, also add a StreamHandler to the logger. Defaults to True.

    Returns:
        logging.Logger: Configured logger instance.

    This logger uses a RotatingFileHandler, which automatically rotates the log file when it exceeds the specified size (log_max_bytes). Old log files are kept up to log_backup_count backups.
    Log output format: [timestamp] LEVEL logger_name: message
    If add_console_handler is True, logs are also streamed to the console for convenience.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=log_max_bytes, backupCount=log_backup_count)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if add_console_handler:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
    return logger