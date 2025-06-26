"""
Goose Data Export Utilities
"""

import json
import os

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
data_dir = os.path.join(project_root, "data", "goose", "collected")


def save_goose_data(
    song_data: "pd.DataFrame",
    show_data: "pd.DataFrame",
    venue_data: "pd.DataFrame",
    setlist_data: "pd.DataFrame",
    transition_data: "pd.DataFrame",
    next_show_info: dict,
    output_dir: str = data_dir,
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
        next_show_info (dict): Dict with next show info (show_date, venue_name, city, state).
        output_dir (str): Directory to save files. Defaults to DATA_DIR from config.
    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)
    # Write next_show_info dict to next_show.json
    next_show_path = os.path.join(output_dir, "next_show.json")
    if next_show_info and any(next_show_info.values()):
        with open(next_show_path, "w", encoding="utf-8") as f:
            json.dump({"next_show": next_show_info}, f, indent=2)
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
        filepath = os.path.join(output_dir, filename)
        data.to_csv(filepath, index=False)


def save_query_data(output_dir: str = "data/goose") -> None:
    """
    Save the last updated timestamp to a JSON file.

    Args:
        data_dir (str): Directory to save the file. Defaults to DATA_DIR from config.
    Returns:
        None
    """
    last_updated_path = os.path.join(output_dir, "last_updated.json")
    with open(last_updated_path, "w", encoding="utf-8") as f:
        json.dump({"last_updated": get_date_and_time()}, f, indent=2)
