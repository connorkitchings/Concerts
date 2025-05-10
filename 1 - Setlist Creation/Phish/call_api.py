import os
from logger import get_logger

logger = get_logger(__name__)

import requests
import pathlib

# Helper to access credentials from env or file
def access_credentials():
    api_key_env = os.getenv("PHISH_API_KEY")
    if api_key_env:
        return api_key_env
    # Try local path instead
    current_file = pathlib.Path(__file__).resolve()
    credentials_path = current_file.parent.parent.parent.parent / 'Credentials' / 'phish_net.txt'
    try:
        with open(credentials_path) as f:
            return f.readline().strip().split(": ")[1].strip("'")
    except FileNotFoundError:
        logger.error(f"Credentials file not found at {credentials_path}")
    logger.error("API key not found in environment variables or credentials file.")
    raise FileNotFoundError("Phish.net API key not found.")

# Helper to make API requests
def make_api_request(endpoint: str, api_key: str) -> dict:
    url = f"https://api.phish.net/v5/{endpoint}.json?apikey={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()