"""
Phish data export utilities for saving data and timestamps to disk.
All paths and filenames are hardcoded to avoid config dependencies.
"""

import json
import os
from datetime import datetime

import pandas as pd


def get_date_and_time():
    """Returns current time as ISO string (YYYY-MM-DD HH:MM:SS)"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save_phish_data(
    song_data: "pd.DataFrame",
    show_data: "pd.DataFrame",
    venue_data: "pd.DataFrame",
    setlist_data: "pd.DataFrame",
    transition_data: "pd.DataFrame",
    data_dir: str = "data/phish/collected",
) -> None:
    """
    Save Phish data (songs, shows, venues, setlists, transitions) to CSV files
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
    # Save next upcoming show to next_show.json
    today = datetime.today().strftime("%Y-%m-%d")
    next_show = (
        show_data[show_data["showdate"] >= today].sort_values("showdate").head(1)
    )
    next_show_path = os.path.join(data_dir, "next_show.json")
    if not next_show.empty:
        next_show_record = next_show.iloc[0].to_dict()
        # Convert Timestamp or datetime to string for JSON serialization
        if isinstance(next_show_record.get("showdate"), (pd.Timestamp, datetime)):
            next_show_record["showdate"] = str(next_show_record["showdate"].date())
        with open(next_show_path, "w", encoding="utf-8") as f:
            json.dump({"next_show": next_show_record}, f, indent=2)
    else:
        if os.path.exists(next_show_path):
            os.remove(next_show_path)
    # Save all CSVs
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


def save_query_data(data_dir: str = "data/phish/collected") -> None:
    """
    Save the last updated timestamp to a JSON file.

    Args:
        data_dir (str): Directory to save the file. Defaults to DATA_DIR from config.
    Returns:
        None
    """
    update_time = get_date_and_time()
    last_updated_path = os.path.join(data_dir, "last_updated.json")
    with open(last_updated_path, "w", encoding="utf-8") as f:
        json.dump({"last_updated": update_time}, f)
