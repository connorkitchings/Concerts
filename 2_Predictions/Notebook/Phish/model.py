import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta

import pandas as pd
from logger import get_logger

logger = get_logger(__name__)


def aggregate_setlist_features(df, target_showdate):
    """
    Aggregates setlist data by song name for a 1-year window before (not including) the target_showdate.
    Excludes songs played in the last 3 shows and sorts by times_played_last_year descending.
    Args:
        df (pd.DataFrame): Setlist data with 'song', 'showid', and 'showdate'
        target_showdate (str or datetime): Target show date (MM-DD-YYYY or datetime)
    Returns:
        pd.DataFrame: Aggregated features per song (by name)
    """
    if isinstance(target_showdate, str):
        try:
            target_showdate = datetime.strptime(target_showdate, "%Y-%m-%d")
        except ValueError:
            try:
                target_showdate = datetime.strptime(target_showdate, "%m-%d-%Y")
            except ValueError:
                raise ValueError(
                    f"target_showdate '{target_showdate}' does not match '%Y-%m-%d' or '%m-%d-%Y'"
                )
    window_start = target_showdate - timedelta(days=365)
    mask = (df["showdate"] >= window_start) & (df["showdate"] < target_showdate)
    df_in_window = df[mask].copy()

    # Exclude songs played in the last 3 shows (by showdate)
    showdata = (
        df[["showid", "showdate"]]
        .drop_duplicates()
        .sort_values("showdate", ascending=False)
    )
    last_3_shows = showdata.head(3)["showdate"].tolist()

    song_groups = df_in_window.groupby("song").agg(
        {
            "showid": lambda x: set(x),  # set of unique showids
            "showdate": list,  # list of showdates (for other calculations)
        }
    )
    results = []
    for song, row in song_groups.iterrows():
        unique_showids = row["showid"]
        times_played = len(row["showid"])
        play_dates_sorted = sorted(row["showdate"])
        last_time_played_date = play_dates_sorted[-1] if times_played > 0 else None
        window_showids = df_in_window["showid"].sort_values().unique()
        play_show_indices = [
            i for i, sid in enumerate(window_showids) if sid in unique_showids
        ]
        gaps = [j - i for i, j in zip(play_show_indices[:-1], play_show_indices[1:])]
        average_gap = round(sum(gaps) / len(gaps), 3) if gaps else None
        median_gap = round(pd.Series(gaps).median(), 2) if gaps else None
        if times_played > 0:
            last_play_idx = max(play_show_indices)
            current_show_gap = len(window_showids) - 1 - last_play_idx
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
    # Exclude songs played in the last 3 shows
    agg_df = agg_df[~agg_df["last_time_played_date"].isin(last_3_shows)]
    agg_df = agg_df.sort_values("times_played_last_year", ascending=False)
    return agg_df
