"""
Goose Pipeline Configuration

Centralizes all settings for the Goose scraping and data pipeline. Most variables can be overridden with environment variables (see below).
"""
import os
from pathlib import Path
from datetime import datetime

# --- Band and Data Directories ---
BAND_NAME: str = os.environ.get('GOOSE_BAND_NAME', 'Goose')
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR: str = os.environ.get('GOOSE_DATA_DIR', str(PROJECT_ROOT / '3 - Data' / BAND_NAME / 'ElGoose'))
LOG_FILE: str = os.environ.get("GOOSE_LOG_FILE", str(PROJECT_ROOT / 'logs' / 'data_pipeline.log'))

# --- Filenames ---
SONG_DATA_FILENAME: str = os.environ.get('GOOSE_SONG_DATA_FILENAME', 'songdata.csv')
SHOW_DATA_FILENAME: str = os.environ.get('GOOSE_SHOW_DATA_FILENAME', 'showdata.csv')
VENUE_DATA_FILENAME: str = os.environ.get('GOOSE_VENUE_DATA_FILENAME', 'venuedata.csv')
SETLIST_DATA_FILENAME: str = os.environ.get('GOOSE_SETLIST_DATA_FILENAME', 'setlistdata.csv')
TRANSITION_DATA_FILENAME: str = os.environ.get('GOOSE_TRANSITION_DATA_FILENAME', 'transitiondata.csv')
NEXT_SHOW_FILENAME: str = os.environ.get('GOOSE_NEXT_SHOW_FILENAME', 'next_show.json')
LAST_UPDATED_FILENAME: str = os.environ.get('GOOSE_LAST_UPDATED_FILENAME', 'last_updated.json')

# --- Logging ---
LOG_LEVEL: str = os.environ.get('GOOSE_LOG_LEVEL', 'INFO')
LOG_MAX_BYTES: int = int(os.environ.get('GOOSE_LOG_MAX_BYTES', 5 * 1024 * 1024))
LOG_BACKUP_COUNT: int = int(os.environ.get('GOOSE_LOG_BACKUP_COUNT', 5))

# --- Date Formats ---
DATE_FORMAT: str = os.environ.get('GOOSE_DATE_FORMAT', '%m/%d/%Y')
DATETIME_FORMAT: str = os.environ.get('GOOSE_DATETIME_FORMAT', '%Y-%m-%d %H:%M:%S')
