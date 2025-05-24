from UM.config import DATA_DIR, SONG_DATA_FILENAME, VENUE_DATA_FILENAME, SETLIST_DATA_FILENAME, NEXT_SHOW_FILENAME, LAST_UPDATED_FILENAME
from pathlib import Path
import json

def get_date_and_time() -> str:
    """
    Returns the current date and time as a formatted string (MM/DD/YYYY HH:MM).
    Inputs: None
    Outputs: str (formatted date/time)
    """
    from datetime import datetime
    return datetime.now().strftime('%m/%d/%Y %H:%M')


def print_relative_path(path) -> None:
    """
    Print the given file or directory path relative to the first occurrence of 'Concerts/'.
    Accepts either a Path or string. If 'Concerts/' is not found, prints the original path.

    Example:
        /Users/you/Desktop/Repositories/Concerts/1 - Setlist Creation/UM/export_data.py
        -> Concerts/1 - Setlist Creation/UM/export_data.py
    """
    from pathlib import Path
    path_str = str(path)
    marker = 'Concerts' + '/'
    idx = path_str.find(marker)
    if idx == -1:
        marker = 'Concerts' + '\\'
        idx = path_str.find(marker)
    if idx == -1:
        marker = 'Concerts'
        idx = path_str.find(marker)
    if idx != -1:
        print(path_str[idx:])
    else:
        print(path_str)

def get_last_update_time(data_dir: Path = None) -> str:
    """
    Returns the last update time from last_updated.json in the given directory, or None if not found.
    Args:
        data_dir (Path): Directory containing last_updated.json.
    Returns:
        str: Last update time as string, or None if not found.
    """
    last_updated_path = (data_dir or Path(DATA_DIR)) / LAST_UPDATED_FILENAME
    if last_updated_path.exists():
        with open(last_updated_path, "r") as f:
            meta = json.load(f)
            return meta.get("last_updated")
    return None
