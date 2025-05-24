import json
from pathlib import Path
from typing import Dict
import pandas as pd


def get_next_show_info(band: str) -> dict:
    """Read the next_show.json for the given band and return its contents as a dict. For Phish, also merge with venuedata.csv to return date, venue, city, and state."""
    path = Path(f"Data/{band}/From Web/next_show.json")
    if not path.exists():
        return {}
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            show_info = data.get("next_show", {})
    except Exception:
        return {}
    # For Phish, merge with venuedata.csv to get venue, city, state
    if band == "Phish" and show_info and "venueid" in show_info:
        venue_path = Path(f"Data/{band}/From Web/venuedata.csv")
        if venue_path.exists():
            try:
                venues = pd.read_csv(venue_path, dtype={"venueid": str})
                # venueid in show_info may be int or str, ensure both are str for merge
                show_venueid = str(show_info["venueid"])
                venue_row = venues[venues["venueid"].astype(str) == show_venueid]
                if not venue_row.empty:
                    venue_row = venue_row.iloc[0]
                    return {
                        "date": show_info.get("showdate", ""),
                        "venue": venue_row["venue"],
                        "city": venue_row["city"],
                        "state": venue_row["state"]
                    }
            except Exception:
                pass
        # fallback: just return showdate
        return {"date": show_info.get("showdate", "")}
    return show_info


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
