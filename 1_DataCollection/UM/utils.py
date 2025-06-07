from UM.config import DATA_COLLECTED_DIR, LAST_UPDATED_FILENAME
from pathlib import Path
import json
from datetime import datetime
import common_config # For DATETIME_FORMAT

def get_date_and_time() -> str:
    """
    Returns the current date and time as a formatted string using common_config.DATETIME_FORMAT.
    Inputs: None
    Outputs: str (formatted date/time)
    """
    return datetime.now().strftime(common_config.DATETIME_FORMAT)


def print_relative_path(path) -> None:
    """
    Print the given file or directory path relative to the first occurrence of 'Concerts/'.
    Accepts either a Path or string. If 'Concerts/' is not found, prints the original path.

    Example:
        /Users/you/Desktop/Repositories/Concerts/1 - Setlist Creation/UM/export_data.py
        -> Concerts/1 - Setlist Creation/UM/export_data.py
    """
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

def get_last_update_time(data_dir: Path | None = None) -> str | None:
    """
    Returns the last update time from last_updated.json in the given directory, or None if not found.
    Args:
        data_dir (Path): Directory containing last_updated.json.
    Returns:
        str | None: Last update time as string, or None if not found.
    """
    last_updated_path = (data_dir or Path(DATA_COLLECTED_DIR)) / LAST_UPDATED_FILENAME
    if last_updated_path.exists():
        with open(last_updated_path, "r") as f:
            meta = json.load(f)
            return meta.get("last_updated")
    return None
