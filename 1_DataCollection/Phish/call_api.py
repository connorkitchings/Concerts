import os
from logger import get_logger
from Phish.config import LOG_FILE_PATH

logger = get_logger(__name__, log_file=LOG_FILE_PATH, add_console_handler=True)
import requests
import pathlib

# Helper to make API requests
def make_api_request(endpoint: str, api_key: str) -> dict:
    url = f"https://api.phish.net/v5/{endpoint}.json?apikey={api_key}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()