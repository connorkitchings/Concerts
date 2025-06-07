import logging
import os
from logging.handlers import RotatingFileHandler

def restrict_to_repo_root(path: str) -> str:
    """
    Restrict a file or folder path to start from the top-level 'Concerts' folder.
    This makes logs portable regardless of where the repository is stored.

    Args:
        path (str): The absolute or relative file/folder path.

    Returns:
        str: The path starting from the top-level 'Concerts' folder, or the original path if 'Concerts' is not found.
    """
    norm_path = os.path.normpath(path)
    parts = norm_path.split(os.sep)
    if 'Concerts' in parts:
        idx = parts.index('Concerts')
        return os.sep.join(parts[idx:])
    return path

def get_logger(name=None):
    """
    Returns a logger that writes to logs/CK+/notebook.log and also outputs to console.
    Usage: logger = get_logger(__name__)
    """
    # Compute the log directory relative to this file's parent (Notebook)
    log_dir = '/Users/connorkitchings/Desktop/Repositories/Concerts/logs/'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'ck+.log')

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers in subprocesses or reruns
    if not logger.handlers:
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger
