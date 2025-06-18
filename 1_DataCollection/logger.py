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
from pathlib import Path  # Added for Path type hint
from typing import Union  # To allow Path or str for log_file

# Import common configuration settings
import common_config

# The restrict_to_repo_root function has been removed as common_config.LOG_FILE_PATH handles project-relative logging.


def get_logger(
    name: str,
    log_file: Union[str, Path] = common_config.LOG_FILE_PATH,
    log_level: str = common_config._log_level_str,  # Use string representation from common_config
    log_max_bytes: int = common_config.LOG_MAX_BYTES,
    log_backup_count: int = common_config.LOG_BACKUP_COUNT,
    add_console_handler: bool = True,
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
    # Ensure log directory exists
    log_file_path = Path(log_file)  # Ensure it's a Path object
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger: logging.Logger = logging.getLogger(name)
    # Set level from string (e.g., 'INFO', 'DEBUG') or use default from common_config if string is invalid
    effective_log_level = getattr(logging, log_level.upper(), common_config.LOG_LEVEL)
    logger.setLevel(effective_log_level)
    if not logger.handlers:
        handler = RotatingFileHandler(
            str(log_file_path), maxBytes=log_max_bytes, backupCount=log_backup_count
        )  # RotatingFileHandler expects a string path
        formatter = logging.Formatter(
            "[%(asctime)s,%(msecs)03d] %(levelname)s %(name)s: %(message)s",
            datefmt="%m-%d-%Y %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if add_console_handler:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
    return logger
