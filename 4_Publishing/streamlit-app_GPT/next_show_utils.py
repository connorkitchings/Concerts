"""Next show information utilities for Jam Band Nerd app."""

import json
from pathlib import Path
from typing import Optional

import streamlit as st
from formatting import (
    format_next_show_phish_goose,
    format_next_show_um,
    format_next_show_wsp,
)


def get_next_show_info(band: str, bands_dir: Path) -> Optional[str]:
    """
    Get formatted next show information for the specified band.

    Args:
        band: String indicating which band to get next show info for
        bands_dir: Path to the bands directory

    Returns:
        str: Formatted next show information or None if not available
    """
    band_dir = bands_dir / band
    next_show_json_paths = {
        "WSP": band_dir / "EverydayCompanion" / "next_show.json",
        "Phish": band_dir / "PhishNet" / "next_show.json",
        "Goose": band_dir / "ElGoose" / "next_show.json",
        "UM": band_dir / "AllThingsUM" / "next_show.json",
    }

    next_show_path = next_show_json_paths.get(band)
    if not next_show_path or not next_show_path.exists():
        return None

    try:
        with open(next_show_path, "r") as f:
            js = json.load(f)

        data = js.get("next_show", {})
        if not data:
            return None

        if band == "WSP":
            return format_next_show_wsp(data)
        elif band == "UM":
            return format_next_show_um(data)
        elif band == "Goose":
            showdata_path = band_dir / "ElGoose" / "showdata.csv"
            venuedata_path = band_dir / "ElGoose" / "venuedata.csv"
            return format_next_show_phish_goose(
                data, showdata_path, venuedata_path, date_field="show_date"
            )
        elif band == "Phish":
            showdata_path = band_dir / "PhishNet" / "showdata.csv"
            venuedata_path = band_dir / "PhishNet" / "venuedata.csv"
            return format_next_show_phish_goose(
                data, showdata_path, venuedata_path, date_field="showdate"
            )
        else:
            return None
    except json.JSONDecodeError as e:
        st.warning(f"Error parsing next show data for {band}: {str(e)}")
        return None
    except FileNotFoundError as e:
        st.warning(f"Required data file not found for {band}: {str(e)}")
        return None
    except Exception as e:
        st.warning(f"Unexpected error getting next show info for {band}: {str(e)}")
        return None
