"""
Logging utilities for the Phish data collection pipeline. Provides a central get_logger function.
"""

import logging


def get_logger(name: str, log_file: str = None, add_console_handler: bool = True):
    """
    Returns a logger with the given name, file, and console handler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%m--%d--%Y %H:%M:%S"
    )
    if not logger.handlers:
        if log_file is not None:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        if add_console_handler:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            logger.addHandler(ch)
    logger.propagate = False
    return logger
