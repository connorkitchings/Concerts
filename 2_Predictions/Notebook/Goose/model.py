import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta

import pandas as pd
from logger import get_logger

logger = get_logger(__name__)


def aggregate_setlist_features(df, target_show_date):
    """
    Aggregates setlist data by song name for a 1-year window before (not including) the target_show_date.
    Excludes songs played in the last 3 shows and sorts by times_played_last_year descending.
    Args:
        df (pd.DataFrame): Setlist data with 'song', 'show_id', and 'show_date'
        target_show_date (str or datetime): Target show date (MM-DD-YYYY or datetime)
    Returns:
        pd.DataFrame: Aggregated features per song (by name)
    """
    if isinstance(target_show_date, str):
        try:
            target_show_date = datetime.strptime(target_show_date, "%Y-%m-%d")
        except ValueError:
            try:
                target_show_date = datetime.strptime(target_show_date, "%m-%d-%Y")
            except ValueError:
                raise ValueError(
                    f"target_show_date '{target_show_date}' does not match '%Y-%m-%d' or '%m-%d-%Y'"
                )
    window_start = target_show_date - timedelta(days=365)
    mask = (df["show_date"] >= window_start) & (df["show_date"] < target_show_date)
    df_in_window = df[mask].copy()

    # Exclude songs played in the last 3 shows (by show_date)
    showdata = (
        df[["show_id", "show_date"]]
        .drop_duplicates()
        .sort_values("show_date", ascending=False)
    )
    last_3_shows = showdata.head(3)["show_date"].tolist()

    song_groups = df_in_window.groupby("song").agg(
        {
            "show_id": lambda x: set(x),  # set of unique show_ids
            "show_date": list,  # list of show_dates (for other calculations)
        }
    )
    results = []
    for song, row in song_groups.iterrows():
        debug_song = "x"
        if song == debug_song:  # Debugging mechanism
            logger.debug(f"Length of show dates: {len(row['show_date'])}")
            logger.debug(f"Show dates for '{debug_song}': {row['show_date']}")
            logger.debug(f"Length of show ids: {len(row['show_id'])}")
            print(f"DEBUG: Show ids for '{debug_song}': {row['show_id']}")
        unique_show_ids = row["show_id"]
        times_played = len(row["show_id"])
        play_dates_sorted = sorted(row["show_date"])
        last_time_played_date = play_dates_sorted[-1] if times_played > 0 else None
        window_show_ids = df_in_window["show_id"].sort_values().unique()
        play_show_indices = [
            i for i, sid in enumerate(window_show_ids) if sid in unique_show_ids
        ]
        gaps = [j - i for i, j in zip(play_show_indices[:-1], play_show_indices[1:])]
        average_gap = round(sum(gaps) / len(gaps), 3) if gaps else None
        median_gap = round(pd.Series(gaps).median(), 2) if gaps else None
        if times_played > 0:
            last_play_idx = max(play_show_indices)
            current_show_gap = len(window_show_ids) - 1 - last_play_idx
        else:
            current_show_gap = None
        results.append(
            {
                "song": song,
                "times_played_last_year": times_played,
                "last_time_played_date": last_time_played_date,
                "current_show_gap": current_show_gap,
                "average_gap": average_gap,
                "median_gap": median_gap,
            }
        )
    agg_df = pd.DataFrame(results)
    agg_df = agg_df[~agg_df["last_time_played_date"].isin(last_3_shows)].sort_values(
        "times_played_last_year", ascending=False
    )
    return agg_df
