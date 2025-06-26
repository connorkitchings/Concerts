import logging

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s', datefmt='%m-%d-%Y %H:%M:%S,%f')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

def restrict_to_repo_root(path=None):
    # Compatibility: just return the path as string, or empty string
    return str(path) if path is not None else ''
