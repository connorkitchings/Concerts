"""
Central configuration for WSP setlist creation pipeline.
All consistent variables and constants should be defined here.
"""
import os
from pathlib import Path
from datetime import datetime

def _parse_years(env_val, default):
    if env_val:
        return [int(y) for y in env_val.split(",") if y.strip().isdigit()]
    return default

# --- URLs ---
# Environment: WSP_BASE_URL
BASE_URL = os.environ.get("WSP_BASE_URL", "http://www.everydaycompanion.com/")
SONG_CODES_URL = f"{BASE_URL}asp/songcode.asp"
TOUR_URL_TEMPLATE = f"{BASE_URL}asp/tour{{yy}}.asp"
SETLIST_URL_TEMPLATE = f"{BASE_URL}setlists/{{datecode}}{{letter}}.asp"

# --- Table Indices ---
# Environment: WSP_SONG_CODES_TABLE_IDX, WSP_SETLIST_TABLE_IDX
SONG_CODES_TABLE_IDX = int(os.environ.get("WSP_SONG_CODES_TABLE_IDX", 3))
SETLIST_TABLE_IDX = int(os.environ.get("WSP_SETLIST_TABLE_IDX", 4))

# --- Band and Data Directories ---
BAND_NAME: str = os.environ.get("WSP_BAND_NAME", "WSP")
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR: str = os.environ.get("WSP_DATA_DIR", str(PROJECT_ROOT / '3 - Data' / BAND_NAME / 'EverydayCompanion'))
LOG_DIR: str = os.environ.get("WSP_LOG_DIR", str(PROJECT_ROOT / 'logs' / 'Setlist_Creation' / BAND_NAME))
LOG_FILE: str = os.environ.get("WSP_LOG_FILE", str(Path(LOG_DIR) / f"data_pipeline.log"))

# --- Logging ---
LOG_LEVEL: str = os.environ.get("WSP_LOG_LEVEL", "INFO")
LOG_MAX_BYTES: int = int(os.environ.get("WSP_LOG_MAX_BYTES", 5 * 1024 * 1024))
LOG_BACKUP_COUNT: int = int(os.environ.get("WSP_LOG_BACKUP_COUNT", 5))

# --- Filenames ---
SONG_DATA_FILENAME = os.environ.get('WSP_SONG_DATA_FILENAME', 'songdata.csv')
SHOW_DATA_FILENAME = os.environ.get('WSP_SHOW_DATA_FILENAME', 'showdata.csv')
SETLIST_DATA_FILENAME = os.environ.get('WSP_SETLIST_DATA_FILENAME', 'setlistdata.csv')
NEXT_SHOW_FILENAME = os.environ.get('WSP_NEXT_SHOW_FILENAME', 'next_show.json')
LAST_UPDATED_FILENAME = os.environ.get('WSP_LAST_UPDATED_FILENAME', 'last_updated.json')

# --- Logging ---
LOG_LEVEL = os.environ.get('WSP_LOG_LEVEL', 'INFO')
LOG_MAX_BYTES = int(os.environ.get('WSP_LOG_MAX_BYTES', 5_000_000))
LOG_BACKUP_COUNT = int(os.environ.get('WSP_LOG_BACKUP_COUNT', 3))

# --- Scraping ---
default_years = [1986, datetime.now().year]
SCRAPE_YEARS = _parse_years(os.environ.get('WSP_SCRAPE_YEARS'), default_years)
SKIP_YEARS = [int(y) for y in os.environ.get('WSP_SKIP_YEARS', '2004').split(',') if y.strip().isdigit()]

# --- Date Formats ---
DATE_FORMAT = os.environ.get('WSP_DATE_FORMAT', '%m/%d/%Y')
DATETIME_FORMAT = os.environ.get('WSP_DATETIME_FORMAT', '%Y-%m-%d %H:%M:%S')

# --- Other ---
FOOTNOTE_PATTERN = os.environ.get('WSP_FOOTNOTE_PATTERN', r"\[(.*?)\]")
