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
        "WSP": band_dir / "collected" / "next_show.json",
        "Phish": band_dir / "collected" / "next_show.json",
        "Goose": band_dir / "collected" / "next_show.json",
        "UM": band_dir / "collected" / "next_show.json",
    }

    next_show_path = next_show_json_paths.get(band)
    if not next_show_path or not next_show_path.exists():
        return None

    try:
        with open(next_show_path, "r") as f:
            js = json.load(f)

        next_show = js.get("next_show", {})
        if not next_show:
            if band == "WSP":
                from datetime import datetime
                today = datetime.now().date()
                date_27 = datetime(2025, 6, 27).date()
                date_29 = datetime(2025, 6, 29).date()
                if today <= date_27:
                    date_str = "06/27/2025"
                elif date_27 < today <= date_29:
                    date_str = today.strftime("%m/%d/%Y")
                else:
                    return None
                return f"Next show: {date_str} at Red Rocks Amphitheater in Morrison, CO"
            return None

        show_date = next_show.get("show_date")
        venue_name = next_show.get("venue_name")
        city = next_show.get("city")
        state = next_show.get("state")

        if band in ("Phish", "Goose"):
            showdata_path = band_dir / "generated" / "showdata.csv"
            venuedata_path = band_dir / "generated" / "venuedata.csv"
            data = {
                "show_date": show_date,
                "venue_name": venue_name,
                "city": city,
                "state": state,
            }
            return format_next_show_phish_goose(
                data, showdata_path, venuedata_path, date_field="show_date"
            )
        elif band == "UM":
            return format_next_show_um(next_show)
        elif band == "WSP":
            return format_next_show_wsp(next_show)
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
