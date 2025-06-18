"""Band-specific utilities for Jam Band Nerd app."""

from pathlib import Path
from typing import Dict, List


def list_band_folders(bands_dir: Path) -> List[str]:
    """List band folders in the data directory.

    Args:
        bands_dir (Path): Path to the data directory.
    Returns:
        List[str]: List of band folder names.
    """
    return [f.name for f in bands_dir.iterdir() if f.is_dir()]


def get_prediction_file_map(band_dir: Path) -> Dict[str, Path]:
    """Return a map of canonical labels ('CK+', 'Notebook') to file paths if present for the band.

    Args:
        band_dir (Path): Path to the band directory.
    Returns:
        Dict[str, Path]: {'CK+': path, 'Notebook': path}
    """
    file_map: Dict[str, Path] = {}
    for f in band_dir.glob("*.csv"):
        fname = f.name.lower()
        if fname == "todaysckplus.csv":
            file_map["CK+"] = f  # Always map todaysckplus.csv to 'CK+'
        elif "ck+" in fname and "ck+" not in file_map:
            file_map["CK+"] = f  # Only map other CK+ files if not already set
        elif "notebook" in fname:
            file_map["Notebook"] = f
    return file_map
