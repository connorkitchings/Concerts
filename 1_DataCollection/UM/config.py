"""
Central configuration for UM setlist creation pipeline.
All consistent variables and constants should be defined here.
"""

import os
from datetime import datetime
from pathlib import Path

# Import common configuration settings
import common_config


def _parse_years(env_val, default):
    if env_val:
        return [int(y) for y in env_val.split(",") if y.strip().isdigit()]
    return default


# --- URLs ---
# Type hints for URL strings
# Environment: UM_BASE_URL
BASE_URL: str = os.environ.get("UM_BASE_URL", "https://allthings.umphreys.com")
SONG_LIST_URL: str = f"{BASE_URL}/song/"
VENUES_URL: str = f"{BASE_URL}/venues/"
SETLISTS_URL_TEMPLATE: str = f"{BASE_URL}/setlists/{{year}}"

# --- Table Indices ---
# Type hints for table indices
# Environment: UM_SONG_TABLE_IDX, UM_VENUE_TABLE_IDX
SONG_TABLE_IDX: int = int(os.environ.get("UM_SONG_TABLE_IDX", 1))
VENUE_TABLE_IDX: int = int(os.environ.get("UM_VENUE_TABLE_IDX", 0))

# --- Band and Data Directories ---
# Type hints for band and data directories
BAND_NAME: str = os.environ.get("UM_BAND_NAME", "UM")
# PROJECT_ROOT is now imported from common_config
DATA_COLLECTED_DIR: Path = Path(
    os.environ.get(
        "UM_DATA_DIR",
        str(common_config.PROJECT_ROOT / "3_DataStorage" / BAND_NAME / "Collected"),
    )
)
DATA_META_DIR: Path = Path(
    os.environ.get(
        "UM_DATA_DIR",
        str(common_config.PROJECT_ROOT / "3_DataStorage" / BAND_NAME / "Meta"),
    )
)
# Band-specific log file path
LOG_DIR_NAME: str = os.environ.get("UM_LOG_DIR_NAME", "logs")
LOG_FILENAME: str = os.environ.get("UM_LOG_FILENAME", "um_pipeline.log")
# Band-specific log file path, now rooted in the main project logs directory
# common_config.LOG_DIR_NAME is typically 'logs'
# BAND_NAME is 'UM'
# LOG_FILENAME is 'um_pipeline.log'
# Resulting path: <PROJECT_ROOT>/logs/UM/um_pipeline.log
LOG_FILE_PATH: Path = (
    common_config.PROJECT_ROOT / common_config.LOG_DIR_NAME / BAND_NAME / LOG_FILENAME
)

# --- Filenames ---
# Type hints for filenames
# Environment: UM_SONG_DATA_FILENAME, etc.
SONG_DATA_FILENAME: str = os.environ.get("UM_SONG_DATA_FILENAME", "songdata.csv")
VENUE_DATA_FILENAME: str = os.environ.get("UM_VENUE_DATA_FILENAME", "venuedata.csv")
SETLIST_DATA_FILENAME: str = os.environ.get(
    "UM_SETLIST_DATA_FILENAME", "setlistdata.csv"
)
NEXT_SHOW_FILENAME: str = os.environ.get("UM_NEXT_SHOW_FILENAME", "next_show.json")
LAST_UPDATED_FILENAME: str = os.environ.get(
    "UM_LAST_UPDATED_FILENAME", "last_updated.json"
)

# --- Logging (Defaults imported from common_config, path is band-specific) ---
# LOG_LEVEL is common_config.LOG_LEVEL
# LOG_MAX_BYTES is common_config.LOG_MAX_BYTES
# LOG_BACKUP_COUNT is common_config.LOG_BACKUP_COUNT

# --- Scraping ---
# Type hints for scraping configuration
# Environment: UM_SCRAPE_YEARS (comma-separated, e.g. "2023,2024")
default_years = [datetime.now().year - 1, datetime.now().year]
SCRAPE_YEARS: list[int] = _parse_years(os.environ.get("UM_SCRAPE_YEARS"), default_years)

# --- Date Formats (Imported from common_config) ---
# DATE_FORMAT is common_config.DATE_FORMAT
# DATETIME_FORMAT is common_config.DATETIME_FORMAT

# --- Other ---
# Type hints for other configuration
# Environment: UM_FOOTNOTE_PATTERN
FOOTNOTE_PATTERN: str = os.environ.get("UM_FOOTNOTE_PATTERN", r"\[(.*?)\]")
