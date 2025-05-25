import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from logger import get_logger, restrict_to_repo_root

logger = get_logger(__name__, add_console_handler=True)

from UM.config import BASE_URL, VENUE_TABLE_IDX

def scrape_um_shows(base_url: str = BASE_URL) -> pd.DataFrame:
    """
    Scrape and return UM venue data from allthings.umphreys.com.

    Args:
        base_url (str): Base URL for the UM website (default is BASE_URL).

    Returns:
        pd.DataFrame: DataFrame containing venue data with columns such as 'id', 'Last Played', etc.
    """
    venues_url = f"{base_url}/venues/"
    response = requests.get(venues_url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    if not tables or len(tables) <= VENUE_TABLE_IDX:
        logger.error(f"Expected venue table at index {VENUE_TABLE_IDX} not found in UM venue page.")
        return pd.DataFrame()
    tables_str = str(tables)
    tables_io = StringIO(tables_str)
    tables = pd.read_html(tables_io)
    venue_data = tables[VENUE_TABLE_IDX].copy().reset_index(names='id')
    venue_data['id'] = venue_data['id'].astype(str)
    venue_data['Last Played'] = pd.to_datetime(venue_data['Last Played']).dt.date
    logger.info(f"Scraped {len(venue_data)} venues from {venues_url}")
    return venue_data
