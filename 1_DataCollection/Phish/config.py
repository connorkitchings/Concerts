"""
Phish Pipeline Configuration

Centralizes all settings for the Phish scraping and data pipeline. Most variables can be overridden with environment variables (see below).
"""
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import common configuration settings
import common_config

# --- Band and Data Directories ---
BAND_NAME: str = os.environ.get('PHISH_BAND_NAME', 'Phish')
# PROJECT_ROOT is now imported from common_config
DATA_COLLECTED_DIR: str = os.environ.get('PHISH_DATA_DIR', str(common_config.PROJECT_ROOT / '3_DataStorage' / BAND_NAME / 'Collected'))
DATA_META_DIR: str = os.environ.get('PHISH_DATA_DIR', str(common_config.PROJECT_ROOT / '3_DataStorage' / BAND_NAME / 'Meta'))
# Band-specific log file path
LOG_DIR_NAME: str = os.environ.get('PHISH_LOG_DIR_NAME', 'logs')
LOG_FILENAME: str = os.environ.get('PHISH_LOG_FILENAME', 'phish_pipeline.log')
# Band-specific log file path, now rooted in the main project logs directory
# common_config.LOG_DIR_NAME is typically 'logs'
# BAND_NAME is 'Phish'
# LOG_FILENAME is 'phish_pipeline.log'
# Resulting path: <PROJECT_ROOT>/logs/Phish/phish_pipeline.log
LOG_FILE_PATH: Path = common_config.PROJECT_ROOT / common_config.LOG_DIR_NAME / BAND_NAME / LOG_FILENAME

# --- Filenames ---
SONG_DATA_FILENAME: str = os.environ.get('PHISH_SONG_DATA_FILENAME', 'songdata.csv')
SHOW_DATA_FILENAME: str = os.environ.get('PHISH_SHOW_DATA_FILENAME', 'showdata.csv')
VENUE_DATA_FILENAME: str = os.environ.get('PHISH_VENUE_DATA_FILENAME', 'venuedata.csv')
SETLIST_DATA_FILENAME: str = os.environ.get('PHISH_SETLIST_DATA_FILENAME', 'setlistdata.csv')
TRANSITION_DATA_FILENAME: str = os.environ.get('PHISH_TRANSITION_DATA_FILENAME', 'transitiondata.csv')
NEXT_SHOW_FILENAME: str = os.environ.get('PHISH_NEXT_SHOW_FILENAME', 'next_show.json')
LAST_UPDATED_FILENAME: str = os.environ.get('PHISH_LAST_UPDATED_FILENAME', 'last_updated.json')

# --- Logging (Defaults imported from common_config, path is band-specific) ---
# LOG_LEVEL is common_config.LOG_LEVEL
# LOG_MAX_BYTES is common_config.LOG_MAX_BYTES
# LOG_BACKUP_COUNT is common_config.LOG_BACKUP_COUNT

# --- API Keys ---
load_dotenv()
API_KEY: str = os.environ.get('PHISH_API_KEY', '')

# --- Date Formats (Imported from common_config) ---
# DATE_FORMAT is common_config.DATE_FORMAT
# DATETIME_FORMAT is common_config.DATETIME_FORMAT

# --- Other ---
# Add more config variables as needed
