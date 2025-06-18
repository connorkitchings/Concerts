# /Users/connorkitchings/Desktop/Repositories/Concerts/1_Data_Collection/common_config.py
"""
Common configuration settings for all data collection pipelines.
"""

import logging  # For LOG_LEVEL constants like logging.INFO
import os
from pathlib import Path

# --- Project Root ---
# common_config.py is in 1_Data_Collection.
# PROJECT_ROOT is the parent of 1_Data_Collection, which is 'Concerts'.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Logging ---
LOG_DIR_NAME: str = os.environ.get("LOG_DIR_NAME", "logs")
LOG_FILENAME: str = os.environ.get("LOG_FILENAME", "data_collection.log")
LOG_FILE_PATH: Path = PROJECT_ROOT / LOG_DIR_NAME / LOG_FILENAME

# Default to INFO if the environment variable is not set or invalid
_log_level_str: str = os.environ.get("COMMON_LOG_LEVEL", "INFO").upper()
LOG_LEVEL: int = getattr(logging, _log_level_str, logging.INFO)

LOG_MAX_BYTES: int = int(
    os.environ.get("COMMON_LOG_MAX_BYTES", 5 * 1024 * 1024)
)  # 5 MB
LOG_BACKUP_COUNT: int = int(os.environ.get("COMMON_LOG_BACKUP_COUNT", 5))

# --- Date Formats ---
DATE_FORMAT: str = os.environ.get("COMMON_DATE_FORMAT", "%m/%d/%Y")
DATETIME_FORMAT: str = os.environ.get("COMMON_DATETIME_FORMAT", "%Y-%m-%d %H:%M:%S")


def get_project_root() -> Path:
    """
    Returns the calculated project root directory.

    Returns:
        Path: The absolute path to the project root.
    """
    return PROJECT_ROOT


def get_log_file_path() -> Path:
    """
    Returns the fully constructed log file path and ensures the log directory exists.

    Returns:
        Path: The absolute path to the log file.
    """
    log_dir = LOG_FILE_PATH.parent
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
    return LOG_FILE_PATH
