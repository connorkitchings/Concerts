import json
from pathlib import Path
from typing import Dict

def get_last_updated_times(bands) -> Dict[str, str]:
    """Read the last updated time for each band from its last_updated.json file."""
    last_updated = {}
    for band in bands:
        path = Path(f"Data/{band}/From Web/last_updated.json")
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    last_updated[band] = data.get("last_updated", "Unknown")
            except Exception as e:
                last_updated[band] = f"Error: {e}"
        else:
            last_updated[band] = "Unknown"
    return last_updated
