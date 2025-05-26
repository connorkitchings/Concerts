import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from datetime import datetime
from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features
from logger import get_logger
import json
import argparse

logger = get_logger(__name__)

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


# Paths (same as predict_today.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../3 - Data/Phish/"))
setlist_path = os.path.join(data_folder, "PhishNet/setlistdata.csv")
showdata_path = os.path.join(data_folder, "PhishNet/showdata.csv")
songdata_path = os.path.join(data_folder, "PhishNet/songdata.csv")
prediction_save_dir = os.path.join(data_folder, "Predictions/notebook")
os.makedirs(prediction_save_dir, exist_ok=True)


def evaluate_historical_accuracy(num_shows: int = 50) -> None:
    """
    Evaluate prediction recall and precision over the last `num_shows` shows for both top 25 and top 50 predictions.
    Saves results to a single JSON file with both groups, sorted by showdate descending.
    Args:
        num_shows: Number of most recent shows to evaluate.
    """
    df: pd.DataFrame = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    show_dates: pd.DataFrame = (
        df[['showid', 'showdate']]
        .drop_duplicates()
        .sort_values('showdate')
        .reset_index(drop=True)
    )
    show_dates = show_dates[show_dates['showdate'].notna()]
    target_shows = show_dates.tail(num_shows)
    combined_results: Dict[str, Any] = {}
    for top_n in [25, 50]:
        results: List[Dict[str, Any]] = []
        for idx, row in target_shows.iterrows():
            showid = row['showid']
            showdate = row['showdate']
            logger.info(f"Evaluating show on {showdate.date()} for top_{top_n}")
            df_before = df[df['showdate'] < showdate]
            if df_before.empty:
                logger.warning(f"No data before show on {showdate.date()}, skipping.")
                continue
            agg_df = aggregate_setlist_features(df_before, showdate)
            predicted_songs: List[str] = agg_df['song'].head(top_n).tolist()
            actual_songs: List[str] = (
                df[df['showid'] == showid]['song']
                .dropna()
                .unique()
                .tolist()
            )
            if not actual_songs:
                logger.warning(f"No actual setlist found for show on {showdate.date()}, skipping.")
                continue
            recall = compute_recall_at_n(predicted_songs, actual_songs, top_n)
            precision = compute_precision_at_n(predicted_songs, actual_songs, top_n)
            results.append({
                'showid': str(showid),
                'showdate': str(showdate.date()),
                'recall': round(recall, 5),
                'precision': round(precision, 5)
            })
            logger.info(f"Show {showdate.date()} (top_{top_n}): Recall: {recall:.2%}, Precision: {precision:.2%}")
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
    save_json_path = os.path.join(prediction_save_dir, "notebook_accuracy.json")
    with open(save_json_path, 'w') as f:
        json.dump(combined_results, f, indent=2)
    rel_save_json_path = os.path.relpath(save_json_path, start=os.path.join(os.path.dirname(__file__), '../../../'))
    logger.info(f"Saved combined accuracy and precision results to Concerts/{rel_save_json_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate historical prediction accuracy for both top 25 and top 50 predictions.")
    parser.add_argument("--num_shows", type=int, default=50, help="Number of shows to evaluate")
    args = parser.parse_args()
    evaluate_historical_accuracy(num_shows=args.num_shows)
    rel_top25 = os.path.relpath(os.path.join(prediction_save_dir, 'notebook_accuracy_top25.json'), start=os.path.join(os.path.dirname(__file__), '../../../'))
    rel_top50 = os.path.relpath(os.path.join(prediction_save_dir, 'notebook_accuracy_top50.json'), start=os.path.join(os.path.dirname(__file__), '../../../'))
    print(f"Saved results to Concerts/{rel_top25} and Concerts/{rel_top50}")
