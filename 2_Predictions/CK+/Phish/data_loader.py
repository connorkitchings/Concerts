import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from logger import get_logger, restrict_to_repo_root

logger = get_logger(__name__)


def load_setlist_and_showdata(setlist_path, showdata_path, songdata_path):
    """
    Loads setlist, show, and song data for Phish. Merges show_date and song name into setlist data.
    Returns merged DataFrame with a 'song' column.
    """
    df = pd.read_csv(setlist_path)
    show_df = pd.read_csv(showdata_path, usecols=["showid", "showdate"])
    show_df["showdate"] = pd.to_datetime(show_df["showdate"])
    df = df.merge(show_df, on="showid", how="left")
    song_df = pd.read_csv(songdata_path, usecols=["song_id", "song"])
    df = df.merge(song_df, left_on="songid", right_on="song_id", how="left")
    logger.info(
        f"Loaded setlist ({len(df):,}) rows from {restrict_to_repo_root(setlist_path)}, shows from {restrict_to_repo_root(showdata_path)}, songs from {restrict_to_repo_root(songdata_path)}"
    )
    return df
