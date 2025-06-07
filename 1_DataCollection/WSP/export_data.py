import os
import json
from datetime import datetime, date
from logger import get_logger

logger = get_logger(__name__, add_console_handler=True)

import csv
import pandas as pd

# logger initialized above using get_logger from logger.py
from WSP.config import DATA_COLLECTED_DIR, SONG_DATA_FILENAME, SHOW_DATA_FILENAME, SETLIST_DATA_FILENAME, NEXT_SHOW_FILENAME, LAST_UPDATED_FILENAME

"""
WSP Data Export Script

Handles saving WSP show, song, and setlist data to CSV and JSON files.
All configuration is managed via config.py and environment variables.
"""

def save_wsp_data(song_data: 'pd.DataFrame', show_data: 'pd.DataFrame', setlist_data: 'pd.DataFrame', data_dir: str = DATA_COLLECTED_DIR) -> None:
    """
    Save WSP data (songs, shows, setlists) to CSV files and update JSON files for last updated and next show.

    Args:
        song_data (pd.DataFrame): DataFrame of song data.
        show_data (pd.DataFrame): DataFrame of show data.
        setlist_data (pd.DataFrame): DataFrame of setlist data.
        data_dir (str): Directory to save files. Defaults to DATA_DIR from config.
    Returns:
        None
    """
    os.makedirs(data_dir, exist_ok=True)
    data_pairs = {
        SONG_DATA_FILENAME: song_data,
        SHOW_DATA_FILENAME: show_data,
        SETLIST_DATA_FILENAME: setlist_data
    }
    for filename, data in data_pairs.items():
        filepath = os.path.join(data_dir, filename)
        if filename == SETLIST_DATA_FILENAME:
            data.to_csv(filepath, index=False, quoting=csv.QUOTE_MINIMAL)
        else:
            data.to_csv(filepath, index=False)
    
    # Save last_updated timestamp
    last_updated_path = os.path.join(data_dir, LAST_UPDATED_FILENAME)
    with open(last_updated_path, "w") as f:
        json.dump({"last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, f)
    
    # Update Next Show
    today = datetime.today()
    today_date = today.date()
    next_show_path = os.path.join(data_dir, NEXT_SHOW_FILENAME)
    show_data['date'] = pd.to_datetime(show_data['date'], format='%m/%d/%Y', errors='coerce').dt.date
    future_shows = show_data[show_data['date'] >= today_date].sort_values('date', ascending=True)
    if not future_shows.empty:
        next_show = future_shows.iloc[0]
        logger.info(f"Found next show: {next_show['date']} at {next_show['venue']} in {next_show['city']}, {next_show['state']}")
    else:
        next_show = None
        logger.info("No future shows found in schedule")
    # Ensure JSON serializability for next_show
    if next_show is not None:
        next_show_dict = next_show.to_dict()
        for k, v in next_show_dict.items():
            if isinstance(v, (datetime, date)):
                next_show_dict[k] = v.isoformat()
        json_next_show = next_show_dict
    else:
        json_next_show = None
    with open(next_show_path, "w") as f:
        json.dump({"next_show": json_next_show}, f, indent=2)

