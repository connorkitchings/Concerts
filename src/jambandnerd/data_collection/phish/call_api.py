"""
API helpers for Phish data collection. No config dependencies; loads API key from .env.
"""

import os

import requests
from dotenv import load_dotenv

from .utils import get_logger

# Ensure logs/Phish/ is always relative to the project root, not src/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
logs_dir = os.path.join(project_root, "logs", "Phish")
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "phish_pipeline.log")
logger = get_logger(__name__, log_file=log_file, add_console_handler=True)


def get_api_key() -> str:
    """Load the PHISH_API_KEY from the .env file in the project root."""
    load_dotenv(
        os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            ".env",
        )
    )
    api_key = os.getenv("PHISH_API_KEY")
    if not api_key:
        logger.error("PHISH_API_KEY not found in .env file.")
        raise RuntimeError("PHISH_API_KEY not found in .env file.")
    return api_key


def make_api_request(endpoint: str, api_key: str) -> dict:
    """Make an API request to the Phish API."""
    url = f"https://api.phish.net/v5/{endpoint}.json?apikey={api_key}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()
