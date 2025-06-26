"""Constants and configuration for the Streamlit Jam Band Nerd app."""

from pathlib import Path
from typing import Dict

# Data directory for band data
BANDS_DIR: Path = (Path(__file__).parent.parent.parent / "data").resolve()  # Points to repo-root/data

# Display names for bands
BAND_DISPLAY_NAMES: Dict[str, str] = {
    "Goose": "Goose",
    "Phish": "Phish",
    # "UM": "Umphrey's McGee",  # UM temporarily disabled
    "WSP": "Widespread Panic",
}

# Notebook display labels for each band
NOTEBOOK_LABELS: Dict[str, str] = {
    "Phish": "Trey's Notebook",
    "WSP": "JoJo's Notebook",
    "Goose": "Rick's Notebook",
    # "UM": "Joel's Notebook",  # UM temporarily disabled
}
