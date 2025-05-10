import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from logger import get_logger

logger = get_logger(__name__)


VENUE_TABLE_IDX = 0
BASE_URL = "https://allthings.umphreys.com"

def scrape_um_shows(base_url=BASE_URL):
    """
    Scrape and return UM venue data from allthings.umphreys.com.
    Returns a tuple: (empty DataFrame for show data, DataFrame for venue data).
    """
    venues_url = f"{base_url}/venues/"
    response = requests.get(venues_url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    if not tables or len(tables) <= VENUE_TABLE_IDX:
        logger.error(f"Expected venue table at index {VENUE_TABLE_IDX} not found in UM venue page.")
        return pd.DataFrame(), pd.DataFrame()
    tables_str = str(tables)
    tables_io = StringIO(tables_str)
    tables = pd.read_html(tables_io)
    venue_data = tables[VENUE_TABLE_IDX].copy().reset_index(names='id')
    venue_data['id'] = venue_data['id'].astype(str)
    venue_data['Last Played'] = pd.to_datetime(venue_data['Last Played']).dt.date
    show_data = pd.DataFrame()
    return show_data, venue_data
