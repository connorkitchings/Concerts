"""Timestamp handling utilities for Jam Band Nerd app."""

import json
import os
from datetime import datetime as dt
from pathlib import Path
from typing import Optional, Tuple

import streamlit as st


def get_last_updated_path(band: str, band_dir: Path) -> Optional[Path]:
    """
    Get the path to the last_updated.json file for the specified band.

    Args:
        band: String indicating which band
        band_dir: Path to the band directory

    Returns:
        Path: Path to the last_updated.json file or None if not available
    """
    # All bands now use the same structure: {band}/collected/last_updated.json
    collected_path = band_dir / "collected" / "last_updated.json"
    if collected_path.exists():
        return collected_path
    return None


def parse_timestamp(timestamp_str: str) -> Tuple[str, str]:
    """
    Parse a timestamp string into date and time components.

    Args:
        timestamp_str: String containing a timestamp

    Returns:
        tuple: (date_str, time_str) formatted components
    """
    # Try different timestamp formats
    formats = [
        ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%H:%M:%S"),
        ("%m/%d/%Y %H:%M", "%Y-%m-%d", "%H:%M"),
        # Add more formats as needed
    ]

    for fmt, date_fmt, time_fmt in formats:
        try:
            dt_obj = dt.strptime(timestamp_str, fmt)
            return dt_obj.strftime(date_fmt), dt_obj.strftime(time_fmt)
        except ValueError:
            continue

    # If no format matches, return the original string and empty time
    return timestamp_str, ""


def get_data_collection_timestamp(band: str, band_dir: Path) -> Tuple[str, str]:
    """
    Get the data collection timestamp for the specified band.

    Args:
        band: String indicating which band
        band_dir: Path to the band directory

    Returns:
        tuple: (date_str, time_str) of when data was collected
    """
    last_updated_path = get_last_updated_path(band, band_dir)
    if not last_updated_path or not os.path.exists(last_updated_path):
        return "Unknown", "Unknown"

    try:
        with open(last_updated_path, "r") as f:
            last_updated = json.load(f).get("last_updated", "")
            if not last_updated:
                return "Unknown", "Unknown"

        return parse_timestamp(last_updated)
    except json.JSONDecodeError as e:
        st.warning(f"Error parsing last updated data: {str(e)}")
        return "Unknown", "Unknown"
    except Exception as e:
        st.warning(f"Error reading last updated data: {str(e)}")
        return "Unknown", "Unknown"


def get_prediction_timestamp(band_dir: Path, file_label: str) -> Tuple[str, str]:
    """
    Get the prediction timestamp for the specified prediction method.

    Args:
        band_dir: Path to the band directory
        file_label: String indicating prediction method

    Returns:
        tuple: (date_str, time_str) of when prediction was made
    """
    date_updated_path = band_dir / "generated" / "date_updated.json"
    if not os.path.exists(date_updated_path):
        return "Unknown", "Unknown"

    try:
        with open(date_updated_path, "r") as f:
            date_updates = json.load(f)

        # Try all common label variants for robustness
        label_variants = [file_label, file_label.lower(), file_label.upper(), file_label.capitalize()]
        if file_label.lower() == "notebook":
            label_variants += ["Notebook", "notebook"]
        if file_label.lower() == "ck+":
            label_variants += ["CK+", "ck+"]
        pred_dt = None
        for variant in label_variants:
            for key in date_updates:
                if key.lower() == variant.lower():
                    pred_dt = date_updates[key].get("date_updated", None)
                    break
            if pred_dt:
                break
        if not pred_dt:
            return "Unknown", "Unknown"
        # Try ISO format first, then other formats
        try:
            dt_obj = dt.fromisoformat(pred_dt)
            return dt_obj.strftime("%Y-%m-%d"), dt_obj.strftime("%H:%M:%S")
        except ValueError:
            return parse_timestamp(pred_dt)

    except json.JSONDecodeError as e:
        st.warning(f"Error parsing prediction timestamp data: {str(e)}")
        return "Unknown", "Unknown"
    except Exception as e:
        st.warning(f"Error reading prediction timestamp: {str(e)}")
        return "Unknown", "Unknown"
