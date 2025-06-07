import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from logger import get_logger
from UM.config import BASE_URL, SONG_TABLE_IDX, LOG_FILE_PATH # Added LOG_FILE_PATH

logger = get_logger(__name__, log_file=LOG_FILE_PATH, add_console_handler=True) # Updated logger

def scrape_um_songs(base_url: str = BASE_URL) -> pd.DataFrame:
    """
    Scrape and return the UM song catalog from allthings.umphreys.com.

    Args:
        base_url (str): Base URL for the UM website (default is BASE_URL).

    Returns:
        pd.DataFrame: DataFrame containing song metadata.
    """
    songlist_url = f"{base_url}/song/"
    response = requests.get(songlist_url, timeout=60) # Added timeout
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    if not tables or len(tables) <= SONG_TABLE_IDX:
        logger.error(f"Expected song table at index {SONG_TABLE_IDX} not found in UM song page.")
        return pd.DataFrame()
    tables_str = str(tables)
    tables_io = StringIO(tables_str)
    tables = pd.read_html(tables_io)
    songlist_data = tables[SONG_TABLE_IDX].copy().sort_values(by='Song Name').reset_index(drop=True)
    songlist_data['Debut Date'] = pd.to_datetime(songlist_data['Debut Date']).dt.date
    songlist_data['Last Played'] = pd.to_datetime(songlist_data['Last Played']).dt.date
    return songlist_data
