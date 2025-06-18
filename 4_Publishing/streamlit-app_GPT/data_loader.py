"""Data loading and processing utilities for Jam Band Nerd app."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
from constants import NOTEBOOK_LABELS


def load_prediction_csv(csv_path: Path) -> pd.DataFrame:
    """Load a prediction CSV as a DataFrame.

    Args:
        csv_path: Path to CSV file
    Returns:
        pd.DataFrame: Loaded DataFrame
    """
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"Failed to load {csv_path.name}: {e}")
        return pd.DataFrame()


def format_dataframe(
    df: pd.DataFrame, expected_cols: List[str], display_cols: List[str]
) -> pd.DataFrame:
    """
    Format a dataframe by selecting expected columns and renaming them.

    Args:
        df: pandas DataFrame to format
        expected_cols: List of source column names to select
        display_cols: List of display column names to rename to

    Returns:
        pd.DataFrame: Formatted dataframe with selected and renamed columns
    """
    # Filter to only include columns that exist
    available_cols = [col for col in expected_cols if col in df.columns]
    if not available_cols:
        st.warning("No expected columns found in the data.")
        return df

    # Select and rename columns
    result = df[available_cols].copy()
    result.columns = display_cols[: len(available_cols)]
    result.index = range(1, len(result) + 1)
    result.index.name = "Rank"
    return result


def get_column_config(file_label: str, band: str) -> Tuple[str, List[str], List[str]]:
    """
    Get the appropriate column configuration based on prediction method and band.

    Args:
        file_label: String indicating prediction method ("CK+" or "Notebook")
        band: String indicating which band

    Returns:
        tuple: (display_label, expected_columns, display_columns)
    """
    if file_label == "CK+":
        display_label = "CK+"
        expected_columns = [
            "song",
            "times_played",
            "ltp_date",
            "current_gap",
            "avg_gap",
            "gap_ratio",
            "gap_z_score",
            "ck+_score",
        ]
        display_columns = [
            "Song",
            "Times Played Overall",
            "LTP Date",
            "Current Gap",
            "Avg Gap",
            "Gap Ratio",
            "Gap Zscore",
            "CK+ Score",
        ]
    elif file_label == "Notebook":
        display_label = NOTEBOOK_LABELS.get(band, "Notebook")
        if band == "WSP":
            expected_columns = [
                "song",
                "times_played_last_2years",
                "last_time_played_date",
                "current_show_gap",
                "average_gap",
                "median_gap",
            ]
            display_columns = [
                "Song",
                "Times Played Last 2 Years",
                "LTP Date",
                "Current Gap",
                "Average Gap",
                "Median Gap",
            ]
        elif band == "UM":
            expected_columns = [
                "song",
                "times_played_last_year",
                "last_time_played",
                "average_gap_days",
                "median_gap_days",
            ]
            display_columns = [
                "Song",
                "Times Played Last Year",
                "LTP Date",
                "Average Gap",
                "Median Gap",
            ]
        else:
            expected_columns = [
                "song",
                "times_played_last_year",
                "last_time_played_date",
                "current_show_gap",
                "average_gap",
                "median_gap",
            ]
            display_columns = [
                "Song",
                "Times Played Last Year",
                "LTP Date",
                "Current Gap",
                "Average Gap",
                "Median Gap",
            ]
    else:
        display_label = file_label
        # Default columns if needed
        expected_columns = [
            "song",
            "times_played_last_year",
            "last_time_played_date",
            "current_show_gap",
            "average_gap",
            "median_gap",
        ]
        display_columns = [
            "Song",
            "Times Played Last Year",
            "LTP Date",
            "Current Gap",
            "Average Gap",
            "Median Gap",
        ]

    return display_label, expected_columns, display_columns
