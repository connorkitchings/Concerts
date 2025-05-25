"""Band-specific utilities for Jam Band Nerd app."""
from pathlib import Path
from typing import List, Dict

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
    predictions_dir = band_dir / "Predictions"
    file_map: Dict[str, Path] = {}
    if predictions_dir.exists():
        for f in predictions_dir.glob("*.csv"):
            fname = f.name.lower()
            if "ck+" in fname:
                file_map["CK+"] = f
            elif "notebook" in fname:
                file_map["Notebook"] = f
    return file_map
