"""
Goose utility functions for logging, directory management, and time formatting.
"""

import logging
from datetime import datetime
from pathlib import Path


def get_band_data_dir(band_name: str, subfolder: str = "collected") -> Path:
    """
    Returns the path to the band's data directory for a given subfolder.
    For Goose, returns <PROJECT_ROOT>/data/goose.
    """
    root = Path(__file__).resolve().parent.parent.parent.parent
    if band_name.lower() == "goose":
        return root / "data" / "goose"
    return root / "data" / band_name / subfolder


def get_logger(name: str, log_file: Path = None, add_console_handler: bool = True):
    """
    Returns a logger with the given name, file, and console handler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # Use mm--dd--yyyy hh:mm:ss format
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%m--%d--%Y %H:%M:%S"
    )
    # Prevent double logging by only adding handlers if none exist
    if not logger.handlers:
        if log_file is not None:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        if add_console_handler:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            logger.addHandler(ch)
    # Prevent log messages from propagating to the root logger (avoids double logging)
    logger.propagate = False
    return logger


def get_date_and_time() -> str:
    """
    Returns the current date and time as a formatted string.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def print_relative_path(path: Path):
    """
    Prints the given path relative to the current working directory.
    """
    print(str(path.relative_to(Path.cwd())))
