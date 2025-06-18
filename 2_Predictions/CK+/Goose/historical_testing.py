import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # for logger.py in CK+
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)  # for prediction_utils, if needed
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from data_loader import load_setlist_and_showdata
from logger import get_logger, restrict_to_repo_root
from model import aggregate_setlist_features


def compute_precision_at_n(predicted: List[str], actual: List[str], n: int) -> float:
    """
    Compute precision@N for a single show.
    Args:
        predicted: List of predicted song names, ranked by likelihood.
        actual: List of actual song names played in the show.
        n: Number of top predictions to consider.
    Returns:
        Precision@N: Fraction of top-N predictions that are in the actual setlist.
    """
    if not predicted or n == 0:
        return 0.0
    top_n_predicted = predicted[:n]
    return sum(1 for song in top_n_predicted if song in actual) / n


def compute_recall_at_n(predicted: List[str], actual: List[str], n: int) -> float:
    """
    Compute recall@N for a single show (fraction of actual songs in top-N predictions).
    Args:
        predicted: List of predicted song names, ranked by likelihood.
        actual: List of actual song names played in the show.
        n: Number of top predictions to consider.
    Returns:
        Recall@N: Fraction of actual setlist songs that are in the top-N predictions.
    """
    if not actual:
        return 0.0
    top_n_predicted = predicted[:n]
    return sum(1 for song in actual if song in top_n_predicted) / len(actual)


def evaluate_historical_accuracy(num_shows: int = 50) -> None:
    """
    Evaluate prediction recall and precision over the last `num_shows` shows for both top 25 and top 50 predictions.
    Saves results to a single JSON file with both groups, sorted by showdate descending.
    Args:
        num_shows: Number of most recent shows to evaluate.
    """
    logger = get_logger(__name__)
    SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    data_folder = SCRIPT_DIR.parent.parent.parent / "3_DataStorage/Goose/Collected"
    setlist_path = data_folder / "setlistdata.csv"
    showdata_path = data_folder / "showdata.csv"
    songdata_path = data_folder / "songdata.csv"
    meta_dir = SCRIPT_DIR.parent.parent.parent / "3_DataStorage/Goose/Meta/ckplus"
    meta_dir.mkdir(parents=True, exist_ok=True)
    # Load setlist data
    df = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    show_order = (
        df[["show_id", "show_date"]]
        .drop_duplicates()
        .sort_values("show_date")
        .reset_index(drop=True)
    )
    show_order["show_num"] = show_order.index + 1
    df = df.merge(show_order[["show_id", "show_num"]], on="show_id", how="left")
    # Get most recent N shows
    recent_shows = show_order.sort_values("show_date", ascending=False).head(num_shows)
    results = {25: [], 50: []}
    for top_n in [25, 50]:
        for _, show in recent_shows.iterrows():
            showid = show["show_id"]
            showdate = show["show_date"]
            show_df = df[df["show_id"] == showid].copy()
            # Ensure 'show_num' exists in show_df
            if "show_num" not in show_df.columns:
                show_num_val = show_order.loc[
                    show_order["show_id"] == showid, "show_num"
                ]
                if not show_num_val.empty:
                    show_df["show_num"] = show_num_val.values[0]
            actual = show_df["song"].tolist()
            # Use CK+ model to generate predictions for this show
            showdate = show["show_date"]
            historical_df = df[df["show_date"] <= showdate]
            pred_df = aggregate_setlist_features(historical_df)
            predicted = pred_df["song"].tolist()[:top_n]
            recall = compute_recall_at_n(predicted, actual, top_n)
            precision = compute_precision_at_n(predicted, actual, top_n)
            results[top_n].append(
                {
                    "show_id": showid,
                    "show_date": str(showdate),
                    "recall": recall,
                    "precision": precision,
                }
            )
            # Only log the date part (YYYY-MM-DD)
            date_str = str(showdate)[:10]
            log_msg = f"[Top {top_n}] Show {date_str}: Recall={recall:.3f}, Precision={precision:.3f}"
            logger.info(log_msg)
            print(log_msg)
        # Sort results by showdate descending
        results[top_n] = sorted(
            results[top_n], key=lambda x: x["show_date"], reverse=True
        )
    # Save results
    combined_results = {"top_25": results[25], "top_50": results[50]}
    with open(meta_dir / "historical_accuracy.json", "w") as f:
        json.dump(combined_results, f, indent=2)
    rel_save_json_path = restrict_to_repo_root(
        str(meta_dir / "historical_accuracy.json")
    )
    logger.info(
        f"Saved combined accuracy and precision results to {rel_save_json_path}"
    )
    print(f"Saved results to {rel_save_json_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate historical prediction accuracy for CK+ (top 25 and 50)"
    )
    parser.add_argument(
        "--num_shows", type=int, default=50, help="Number of shows to evaluate"
    )
    args = parser.parse_args()
    evaluate_historical_accuracy(num_shows=args.num_shows)
