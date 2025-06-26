"""
Logging utilities for ckplus
"""

import logging
import os
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured logger for the given name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%m-%d-%Y %H:%M:%S,%f",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def restrict_to_repo_root(path: str) -> str:
    """
    Restrict a file or folder path to start from the top-level 'Concerts' folder.
    This makes logs portable regardless of where the repository is stored.

    Args:
        path (str): The absolute or relative file/folder path.

    Returns:
        str: The path starting from the top-level 'Concerts' folder,
        or the original path if 'Concerts' is not found.
    """
    norm_path = os.path.normpath(path)
    parts = norm_path.split(os.sep)
    if "Concerts" in parts:
        idx = parts.index("Concerts")
        return os.sep.join(parts[idx:])
    return path
