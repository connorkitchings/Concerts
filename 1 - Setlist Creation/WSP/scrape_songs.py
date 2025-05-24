import requests
from bs4 import BeautifulSoup
import pandas as pd
from WSP.logger import get_logger
logger = get_logger(__name__)
from io import StringIO

try:
    from export_data import save_wsp_data
except ImportError:
    pass

from WSP.config import SONG_CODES_TABLE_IDX, SONG_CODES_URL

def scrape_wsp_songs(base_url: str = 'http://www.everydaycompanion.com/') -> 'pd.DataFrame':
    """
    Scrape and return the WSP song catalog from everydaycompanion.com.

    Args:
        base_url (str): Base URL for Everyday Companion. Defaults to 'http://www.everydaycompanion.com/'.
    Returns:
        pd.DataFrame: DataFrame with columns ['song', 'code', 'times_played', 'aka', 'ftp', 'ltp'].
    """
    songcode_url = f"{base_url}asp/songcode.asp"
    try:
        response = requests.get(songcode_url)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')
    except Exception as e:
        logger.error(f"Error fetching song codes: {e}", exc_info=True)
        return pd.DataFrame()
    if not tables or len(tables) <= SONG_CODES_TABLE_IDX:
        logger.error(f"Expected table at index {SONG_CODES_TABLE_IDX} not found in song codes page.")
        return pd.DataFrame()
    tables_str = str(tables)
    tables_io = StringIO(tables_str)
    tables = pd.read_html(tables_io)
    song_codes = tables[SONG_CODES_TABLE_IDX].copy()
    song_codes.columns = song_codes.iloc[0]
    song_codes = song_codes[1:].reset_index(drop=True)
    song_codes = song_codes.rename(columns={'Code':'code','Title':'song', 'First': 'ftp', 'Last': 'ltp', 'Times Played': 'times_played', 'Also Known As': 'aka'})
    column = song_codes.pop('song')
    song_codes.insert(0, 'song', column)
    song_codes = song_codes.astype({
        'song': str,
        'code': str,
        'times_played': int
    })
    song_codes['aka'] = song_codes['aka'].fillna('').astype(str)
    song_codes['ftp'] = pd.to_datetime(song_codes['ftp'], format='%m/%d/%y', errors='coerce').dt.strftime('%m/%d/%Y')
    song_codes['ltp'] = pd.to_datetime(song_codes['ltp'], format='%m/%d/%y', errors='coerce').dt.strftime('%m/%d/%Y')
    return song_codes
