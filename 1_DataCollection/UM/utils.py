import json
from pathlib import Path

from UM.config import DATA_COLLECTED_DIR, LAST_UPDATED_FILENAME


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
