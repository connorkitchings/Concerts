"""
Central configuration for UM setlist creation pipeline.
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
# Environment: UM_BASE_URL
BASE_URL = os.environ.get("UM_BASE_URL", "https://allthings.umphreys.com")
SONG_LIST_URL = f"{BASE_URL}/song/"
VENUES_URL = f"{BASE_URL}/venues/"
SETLISTS_URL_TEMPLATE = f"{BASE_URL}/setlists/{{year}}"

# --- Table Indices ---
# Environment: UM_SONG_TABLE_IDX, UM_VENUE_TABLE_IDX
SONG_TABLE_IDX = int(os.environ.get("UM_SONG_TABLE_IDX", 1))
VENUE_TABLE_IDX = int(os.environ.get("UM_VENUE_TABLE_IDX", 0))

# --- Band and Data Directories ---
BAND_NAME = os.environ.get("UM_BAND_NAME", "UM")
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.environ.get("UM_DATA_DIR", str(PROJECT_ROOT / '3 - Data' / BAND_NAME / 'AllThingsUM')))
LOG_FILE = Path(os.environ.get("UM_LOG_FILE", str(PROJECT_ROOT / 'logs' / 'data_pipeline.log')))

# --- Filenames ---
# Environment: UM_SONG_DATA_FILENAME, etc.
SONG_DATA_FILENAME = os.environ.get('UM_SONG_DATA_FILENAME', 'songdata.csv')
VENUE_DATA_FILENAME = os.environ.get('UM_VENUE_DATA_FILENAME', 'venuedata.csv')
SETLIST_DATA_FILENAME = os.environ.get('UM_SETLIST_DATA_FILENAME', 'setlistdata.csv')
NEXT_SHOW_FILENAME = os.environ.get('UM_NEXT_SHOW_FILENAME', 'next_show.json')
LAST_UPDATED_FILENAME = os.environ.get('UM_LAST_UPDATED_FILENAME', 'last_updated.json')

# --- Logging ---
# Environment: UM_LOG_LEVEL, UM_LOG_MAX_BYTES, UM_LOG_BACKUP_COUNT
LOG_LEVEL = os.environ.get('UM_LOG_LEVEL', 'INFO')
LOG_MAX_BYTES = int(os.environ.get('UM_LOG_MAX_BYTES', 5_000_000))
LOG_BACKUP_COUNT = int(os.environ.get('UM_LOG_BACKUP_COUNT', 3))

# --- Scraping ---
# Environment: UM_SCRAPE_YEARS (comma-separated, e.g. "2023,2024")
default_years = [datetime.now().year - 1, datetime.now().year]
SCRAPE_YEARS = _parse_years(os.environ.get('UM_SCRAPE_YEARS'), default_years)

# --- Date Formats ---
# Environment: UM_DATE_FORMAT, UM_DATETIME_FORMAT
DATE_FORMAT = os.environ.get('UM_DATE_FORMAT', '%m/%d/%Y')
DATETIME_FORMAT = os.environ.get('UM_DATETIME_FORMAT', '%Y-%m-%d %H:%M:%S')

# --- Other ---
# Environment: UM_FOOTNOTE_PATTERN
FOOTNOTE_PATTERN = os.environ.get('UM_FOOTNOTE_PATTERN', r"\[(.*?)\]")
