"""
Data loader for Goose prediction pipeline.
Handles loading setlist and show data for predictions.
"""

import os
import sys

import pandas as pd

# Ensure parent directory is in sys.path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger

logger = get_logger(__name__)


def load_setlist_and_showdata(setlist_path, showdata_path, songdata_path):
    """
    Loads setlist, show, and song data. Merges show_date and song name into setlist data.
    Returns merged DataFrame with a 'song' column.
    """
    df = pd.read_csv(setlist_path)
    show_df = pd.read_csv(showdata_path, usecols=["show_id", "show_date"])
    show_df["show_date"] = pd.to_datetime(show_df["show_date"])
    df = df.merge(show_df, on="show_id", how="left")
    song_df = pd.read_csv(songdata_path, usecols=["song_id", "song"])
    df = df.merge(song_df, on="song_id", how="left")
    logger.info(
        f"Loaded setlist ({len(df):,}) rows from {setlist_path}, shows from {showdata_path}, songs from {songdata_path}"
    )
    return df
