import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from datetime import datetime
from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features
import json
import argparse
from logger import get_logger

# Logger is optional, if not present, fallback to print
try:
    logger = get_logger(__name__)
except ImportError:
    logger = None
    def log_info(msg): print(msg)
else:
    def log_info(msg): logger.info(msg)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../3_DataStorage/Goose/"))
setlist_path = os.path.join(data_folder, "Collected/setlistdata.csv")
showdata_path = os.path.join(data_folder, "Collected/showdata.csv")
songdata_path = os.path.join(data_folder, "Collected/songdata.csv")
prediction_save_dir = os.path.join(data_folder, "Meta/notebook")
os.makedirs(prediction_save_dir, exist_ok=True)
from typing import List, Dict, Any

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
    Evaluate prediction accuracy over the last `num_shows` shows for both top 25 and top 50 predictions.
    Saves results to a single JSON file with both groups, sorted by showdate descending.
    """
    df = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    show_dates = (
        df[['show_id', 'show_date']]
        .drop_duplicates()
        .sort_values('show_date')
        .reset_index(drop=True)
    )
    show_dates = show_dates[show_dates['show_date'].notna()]
    target_shows = show_dates.tail(num_shows)
    combined_results = {}
    for top_n in [25, 50]:
        results = []
        for idx, row in target_shows.iterrows():
            showid = row['show_id']
            showdate = row['show_date']
            log_info(f"Evaluating show on {showdate.date()} for top_{top_n}")
            df_before = df[df['show_date'] < showdate]
            if df_before.empty:
                log_info(f"No data before show on {showdate.date()}, skipping.")
                continue
            agg_df = aggregate_setlist_features(df_before, showdate)
            predicted_songs = agg_df['song'].head(top_n).tolist()
            actual_songs = (
                df[df['show_id'] == showid]['song']
                .dropna()
                .unique()
                .tolist()
            )
            if not actual_songs:
                log_info(f"No actual setlist found for show on {showdate.date()}, skipping.")
                continue
            recall = compute_recall_at_n(predicted_songs, actual_songs, top_n)
            precision = compute_precision_at_n(predicted_songs, actual_songs, top_n)
            results.append({
                'showid': str(showid),
                'showdate': str(showdate.date()),
                'recall': round(recall, 5),
                'precision': round(precision, 5)
            })
            log_info(f"Show {showdate.date()} (top_{top_n}): Recall: {recall:.2%}, Precision: {precision:.2%}")
        results_sorted = sorted(results, key=lambda x: x['showdate'], reverse=True)
        if results_sorted:
            overall_recall = round(sum(r['recall'] for r in results_sorted) / len(results_sorted), 5)
            overall_precision = round(sum(r['precision'] for r in results_sorted) / len(results_sorted), 5)
        else:
            overall_recall = None
            overall_precision = None
        combined_results[f'top_{top_n}'] = {
            'most_recent_shows': len(results_sorted),
            'overall_recall': overall_recall,
            'overall_precision': overall_precision,
            'results': results_sorted
        }
    save_json_path = os.path.join(data_folder, "Meta/notebook", "historical_accuracy.json")
    os.makedirs(os.path.dirname(save_json_path), exist_ok=True)
    with open(save_json_path, 'w') as f:
        json.dump(combined_results, f, indent=2)
    rel_save_json_path = os.path.relpath(save_json_path, start=os.path.join(os.path.dirname(__file__), '../../../'))
    log_info(f"Saved combined accuracy and precision results to Concerts/{rel_save_json_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate historical prediction accuracy for both top 25 and top 50 predictions.")
    parser.add_argument("--num_shows", type=int, default=50, help="Number of shows to evaluate")
    args = parser.parse_args()
    evaluate_historical_accuracy(num_shows=args.num_shows)
    rel_json = os.path.relpath(os.path.join(prediction_save_dir, 'notebook_accuracy.json'), start=os.path.join(os.path.dirname(__file__), '../../../'))
    print(f"Saved results to Concerts/{rel_json}")
