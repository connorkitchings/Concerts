import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta

import pandas as pd
from logger import get_logger

logger = get_logger(__name__)


def aggregate_setlist_features(df, target_show_date):
    """
    Aggregates setlist data by song name for a 2-year window before (not including) the target_show_date.
    Excludes songs played in the last 3 shows and sorts by times_played_last_2years descending.
    Args:
        df (pd.DataFrame): Setlist data with 'song', 'show_date'
        target_show_date (str or datetime): Target show date (YYYY-MM-DD or datetime)
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
    window_start = target_show_date - timedelta(days=2 * 365)
    mask = (df["show_date"] >= window_start) & (df["show_date"] < target_show_date)
    df_in_window = df[mask].copy()

    # Exclude songs played in the last 3 shows (by show_date), only considering shows before the target_show_date
    showdata = df[["link", "show_date"]].drop_duplicates()
    showdata = showdata[showdata["show_date"] < target_show_date]
    showdata = showdata.sort_values("show_date", ascending=False)
    last_3_shows = showdata.head(3)["show_date"].tolist()

    song_groups = df_in_window.groupby("song").agg(
        {
            "link": lambda x: set(x),  # set of unique show links
            "show_date": list,  # list of show_dates (for other calculations)
        }
    )
    results = []
    for song, row in song_groups.iterrows():
        unique_show_links = row["link"]
        times_played = len(row["link"])
        play_dates_sorted = sorted(row["show_date"])
        last_time_played_date = play_dates_sorted[-1] if times_played > 0 else None
        window_show_links = df_in_window["link"].sort_values().unique()
        play_show_indices = [
            i for i, sid in enumerate(window_show_links) if sid in unique_show_links
        ]
        gaps = [j - i for i, j in zip(play_show_indices[:-1], play_show_indices[1:])]
        average_gap = round(sum(gaps) / len(gaps), 3) if gaps else None
        median_gap = round(pd.Series(gaps).median(), 2) if gaps else None
        if times_played > 0:
            last_play_idx = max(play_show_indices)
            current_show_gap = len(window_show_links) - 1 - last_play_idx
        else:
            current_show_gap = None
        results.append(
            {
                "song": song,
                "times_played_last_2years": times_played,
                "last_time_played_date": last_time_played_date,
                "current_show_gap": current_show_gap,
                "average_gap": average_gap,
                "median_gap": median_gap,
            }
        )
    features_df = pd.DataFrame(results)
    # Exclude songs played in the last 3 shows
    features_df = features_df[~features_df["last_time_played_date"].isin(last_3_shows)]
    features_df = features_df.sort_values("times_played_last_2years", ascending=False)
    return features_df
