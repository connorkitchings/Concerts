"""
Central configuration for WSP setlist creation pipeline.
All consistent variables and constants should be defined here.
"""
import os
from pathlib import Path
from datetime import datetime

# Import common configuration settings
import common_config

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
# PROJECT_ROOT is now imported from common_config
DATA_COLLECTED_DIR: str = os.environ.get("WSP_DATA_DIR", str(common_config.PROJECT_ROOT / '3_DataStorage' / BAND_NAME / 'Collected'))
DATA_META_DIR: str = os.environ.get("WSP_DATA_DIR", str(common_config.PROJECT_ROOT / '3_DataStorage' / BAND_NAME / 'Meta'))
# --- Logging (Defaults imported from common_config, path is band-specific) ---
# Band-specific log file path
LOG_DIR_NAME: str = os.environ.get('WSP_LOG_DIR_NAME', 'logs')
LOG_FILENAME: str = os.environ.get('WSP_LOG_FILENAME', 'wsp_pipeline.log')
# Band-specific log file path, now rooted in the main project logs directory
# common_config.LOG_DIR_NAME is typically 'logs'
# BAND_NAME is 'WSP'
# LOG_FILENAME is 'wsp_pipeline.log'
# Resulting path: <PROJECT_ROOT>/logs/WSP/wsp_pipeline.log
LOG_FILE_PATH: Path = common_config.PROJECT_ROOT / common_config.LOG_DIR_NAME / BAND_NAME / LOG_FILENAME
# LOG_LEVEL is common_config.LOG_LEVEL
# LOG_MAX_BYTES is common_config.LOG_MAX_BYTES
# LOG_BACKUP_COUNT is common_config.LOG_BACKUP_COUNT

# --- Filenames ---
SONG_DATA_FILENAME = os.environ.get('WSP_SONG_DATA_FILENAME', 'songdata.csv')
SHOW_DATA_FILENAME = os.environ.get('WSP_SHOW_DATA_FILENAME', 'showdata.csv')
SETLIST_DATA_FILENAME = os.environ.get('WSP_SETLIST_DATA_FILENAME', 'setlistdata.csv')
NEXT_SHOW_FILENAME = os.environ.get('WSP_NEXT_SHOW_FILENAME', 'next_show.json')
LAST_UPDATED_FILENAME = os.environ.get('WSP_LAST_UPDATED_FILENAME', 'last_updated.json')
# Redundant logging definitions removed, using common_config now.

# --- Scraping ---
default_years = [1986, datetime.now().year]
SCRAPE_YEARS = _parse_years(os.environ.get('WSP_SCRAPE_YEARS'), default_years)
SKIP_YEARS = [int(y) for y in os.environ.get('WSP_SKIP_YEARS', '2004').split(',') if y.strip().isdigit()]

# --- Date Formats (Imported from common_config) ---
# DATE_FORMAT is common_config.DATE_FORMAT
# DATETIME_FORMAT is common_config.DATETIME_FORMAT

# --- Other ---
FOOTNOTE_PATTERN = os.environ.get('WSP_FOOTNOTE_PATTERN', r"\[(.*?)\]")
