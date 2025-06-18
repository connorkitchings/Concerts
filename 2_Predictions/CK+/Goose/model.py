from datetime import date, timedelta

import pandas as pd
from logger import get_logger

logger = get_logger(__name__)


def aggregate_setlist_features(df, method="mean"):
    # Calculate max show_num in the dataset
    max_show_num = df["show_num"].max()
    # Create gap column
    df = df.sort_values(by=["song", "show_num"], ascending=[True, True])
    df["gap"] = df.groupby("song")["show_num"].diff()

    song_stats = df.groupby("song").agg(
        {
            "show_id": "nunique",
            "show_date": "max",
            "show_num": "max",
            "gap": ["mean", "median", "std"],
        }
    )
    # Flatten columns
    song_stats.columns = [
        "_".join(col).strip() if isinstance(col, tuple) else col
        for col in song_stats.columns.values
    ]
    # Rename columns
    song_stats = song_stats.rename(
        columns={
            "show_id_nunique": "times_played",
            "show_date_max": "ltp_date",
            "show_num_max": "ltp_show_num",
            "gap_mean": "avg_gap",
            "gap_median": "med_gap",
            "gap_std": "std_gap",
        }
    )

    # Calculate Current Gap column for each song
    song_stats["current_gap"] = max_show_num - song_stats["ltp_show_num"]

    # Calculate Gap Variance column for each song
    song_stats["gap_variance"] = song_stats["std_gap"] ** 2

    # Exclude songs last played more than 5 years ago
    song_stats = song_stats[song_stats["current_gap"] < 100]

    # Remove rarities and sort by gap ratio
    song_stats = song_stats[
        (song_stats["times_played"] > 5) & (song_stats["current_gap"] > 0)
    ].reset_index()

    if method == "mean":
        # Calculate Gap Ratio column for each song
        song_stats["gap_ratio"] = song_stats["current_gap"] / song_stats["avg_gap"]
        final_columns = [
            "song",
            "times_played",
            "ltp_date",
            "current_gap",
            "avg_gap",
            "gap_ratio",
            "gap_z_score",
            "ck+_score",
        ]
    elif method == "median":
        song_stats["gap_ratio"] = song_stats["current_gap"] / song_stats["med_gap"]
        final_columns = [
            "song",
            "times_played",
            "ltp_date",
            "current_gap",
            "med_gap",
            "gap_ratio",
            "gap_z_score",
            "ck+_score",
        ]

    # Calculate Gap Z Score column for each song
    song_stats["gap_z_score"] = song_stats["gap_ratio"] / song_stats["std_gap"]

    # Calculate CK+ Score for each song on mean
    song_stats["ck+_score"] = song_stats["gap_z_score"] * song_stats["gap_ratio"]

    # Sort by CK+ Score
    song_stats = song_stats.sort_values(by="ck+_score", ascending=False).reset_index()

    # Only include final columns
    song_stats = song_stats[final_columns]

    # Cut songs to top 50
    song_stats = song_stats.head(50)
    return song_stats
