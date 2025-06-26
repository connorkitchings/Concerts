"""
Goose Data Export Utilities
"""

import json
import os
from datetime import datetime

import pandas as pd

from .utils import get_date_and_time, get_logger

# Ensure logs/Goose/ is always relative to the project root, not src/
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
logs_dir = os.path.join(project_root, "logs", "Goose")
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "goose_pipeline.log")
logger = get_logger(__name__, log_file=log_file, add_console_handler=True)


def save_goose_data(
    song_data: "pd.DataFrame",
    show_data: "pd.DataFrame",
    venue_data: "pd.DataFrame",
    setlist_data: "pd.DataFrame",
    transition_data: "pd.DataFrame",
    data_dir: str = "data/goose/collected",
) -> None:
    """
    Save Goose data (songs, shows, venues, setlists, transitions) to CSV files
    and update JSON files for last updated and next show.

    Args:
        song_data (pd.DataFrame): DataFrame of song data.
        show_data (pd.DataFrame): DataFrame of show data.
        venue_data (pd.DataFrame): DataFrame of venue data.
        setlist_data (pd.DataFrame): DataFrame of setlist data.
        transition_data (pd.DataFrame): DataFrame of transition data.
        data_dir (str): Directory to save files. Defaults to DATA_DIR from config.
    Returns:
        None
    """
    os.makedirs(data_dir, exist_ok=True)
    today = datetime.today().strftime("%Y-%m-%d")
    next_show = (
        show_data[show_data["show_date"] >= today].sort_values("show_date").head(1)
    )
    next_show_path = os.path.join(data_dir, "next_show.json")
    if not next_show.empty:
        next_show_record = next_show.iloc[0].to_dict()
        with open(next_show_path, "w", encoding="utf-8") as f:
            json.dump({"next_show": next_show_record}, f, indent=2)
    else:
        if os.path.exists(next_show_path):
            os.remove(next_show_path)
    data_pairs = {
        "songdata.csv": song_data,
        "showdata.csv": show_data,
        "venuedata.csv": venue_data,
        "setlistdata.csv": setlist_data,
        "transitiondata.csv": transition_data,
    }
    for filename, data in data_pairs.items():
        filepath = os.path.join(data_dir, filename)
        data.to_csv(filepath, index=False)


def save_query_data(data_dir: str = "data/goose") -> None:
    """
    Save the last updated timestamp to a JSON file.

    Args:
        data_dir (str): Directory to save the file. Defaults to DATA_DIR from config.
    Returns:
        None
    """
    last_updated_path = os.path.join(data_dir, "last_updated.json")
    with open(last_updated_path, "w", encoding="utf-8") as f:
        json.dump({"last_updated": get_date_and_time()}, f, indent=2)
