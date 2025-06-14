import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # for logger.py in CK+
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))  # for prediction_utils, if needed
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import json
from pathlib import Path
from logger import get_logger, restrict_to_repo_root
from data_loader import load_setlist_and_showdata
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
    data_folder = SCRIPT_DIR.parent.parent.parent / "3_DataStorage/WSP/Collected"
    setlist_path = data_folder / "setlistdata.csv"
    showdata_path = data_folder / "showdata.csv"
    songdata_path = data_folder / "songdata.csv"
    meta_dir = SCRIPT_DIR.parent.parent.parent / "3_DataStorage/WSP/Meta/ckplus"
    meta_dir.mkdir(parents=True, exist_ok=True)
    # Load setlist data
    df = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    # Use 'link' as show identifier, 'show_date' as date, and 'song' as song name
    show_order = df[['link', 'show_date']].drop_duplicates().sort_values('show_date').reset_index(drop=True)
    show_order['show_index_overall'] = show_order.index + 1
    df = df.merge(show_order[['link', 'show_index_overall']], on='link', how='left')
    # Get most recent N shows
    recent_shows = show_order.sort_values('show_date', ascending=False).head(num_shows)
    results = {25: [], 50: []}
    for top_n in [25, 50]:
        for _, show in recent_shows.iterrows():
            showid = show['link']
            showdate = show['show_date']
            show_df = df[df['link'] == showid]
            actual = show_df['song'].tolist()
            # Use CK+ model to generate predictions for this show
            # Use all data up to and including this show for prediction
            showdate = show['show_date']
            historical_df = df[df['show_date'] <= showdate]
            pred_df = aggregate_setlist_features(historical_df)
            predicted = pred_df['song'].tolist()[:top_n]
            recall = compute_recall_at_n(predicted, actual, top_n)
            precision = compute_precision_at_n(predicted, actual, top_n)
            results[top_n].append({
                'showid': showid,
                'showdate': str(showdate),
                'recall': recall,
                'precision': precision
            })
            # Only log the date part (YYYY-MM-DD)
            date_str = str(showdate)[:10]
            log_msg = f"[Top {top_n}] Show {date_str}: Recall={recall:.3f}, Precision={precision:.3f}"
            logger.info(log_msg)
            print(log_msg)
        # Sort results by showdate descending
        results[top_n] = sorted(results[top_n], key=lambda x: x['showdate'], reverse=True)
    # Save results
    combined_results = {
        'top_25': results[25],
        'top_50': results[50]
    }
    with open(meta_dir / "historical_accuracy.json", "w") as f:
        json.dump(combined_results, f, indent=2)
    rel_save_json_path = restrict_to_repo_root(str(meta_dir / "historical_accuracy.json"))
    logger.info(f"Saved combined accuracy and precision results to {rel_save_json_path}")
    print(f"Saved results to {rel_save_json_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate historical prediction accuracy for CK+ (top 25 and 50)")
    parser.add_argument("--num_shows", type=int, default=50, help="Number of shows to evaluate")
    args = parser.parse_args()
    evaluate_historical_accuracy(num_shows=args.num_shows)
