import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger, restrict_to_repo_root

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
    # Assign sequential show number by show_date
    show_order = (
        df[["show_id", "show_date"]]
        .drop_duplicates()
        .sort_values("show_date")
        .reset_index(drop=True)
    )
    show_order["show_num"] = show_order.index + 1
    df = df.merge(show_order[["show_id", "show_num"]], on="show_id", how="left")
    logger.info(
        f"Loaded ({len(df):,}) rows from {restrict_to_repo_root(setlist_path)}, {len(show_df):,} shows from {restrict_to_repo_root(showdata_path)}, {len(song_df):,} songs from {restrict_to_repo_root(songdata_path)}."
    )
    return df
