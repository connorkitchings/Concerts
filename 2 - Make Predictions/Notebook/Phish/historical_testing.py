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

# Paths (same as predict_today.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../3 - Data/Phish/"))
setlist_path = os.path.join(data_folder, "PhishNet/setlistdata.csv")
showdata_path = os.path.join(data_folder, "PhishNet/showdata.csv")
songdata_path = os.path.join(data_folder, "PhishNet/songdata.csv")
prediction_save_dir = os.path.join(data_folder, "Predictions/")


def evaluate_historical_accuracy(num_shows=50):
    """
    Evaluate prediction accuracy over the last `num_shows` shows for both top 25 and top 50 predictions.
    Saves results to separate files for each top_n value (descending by showdate).
    """
    # Load merged DataFrame
    df = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    # Get all unique shows, sorted by date
    show_dates = (
        df[['showid', 'showdate']]
        .drop_duplicates()
        .sort_values('showdate')
        .reset_index(drop=True)
    )
    show_dates = show_dates[show_dates['showdate'].notna()]
    target_shows = show_dates.tail(num_shows)
    combined_results = {}
    for top_n in [25, 50]:
        results = []
        for idx, row in target_shows.iterrows():
            showid = row['showid']
            showdate = row['showdate']
            logger.info(f"Evaluating show {showid} on {showdate.date()} for top_{top_n}")
            df_before = df[df['showdate'] < showdate]
            if df_before.empty:
                logger.warning(f"No data before show {showid} on {showdate.date()}, skipping.")
                continue
            agg_df = aggregate_setlist_features(df_before, showdate)
            predicted_songs = agg_df['song'].head(top_n).tolist()
            actual_songs = (
                df[df['showid'] == showid]['song']
                .dropna()
                .unique()
                .tolist()
            )
            if not actual_songs:
                logger.warning(f"No actual setlist found for show {showid}, skipping.")
                continue
            accuracy = round(sum(1 for song in actual_songs if song in predicted_songs) / len(actual_songs), 5)
            results.append({
                'showid': str(showid),
                'showdate': str(showdate.date()),
                'accuracy': accuracy
            })
            logger.info(f"Show {showid} (top_{top_n}): {sum(1 for song in actual_songs if song in predicted_songs)}/{len(actual_songs)} correct ({accuracy:.2%})")
        # Sort results by showdate descending
        results_sorted = sorted(results, key=lambda x: x['showdate'], reverse=True)
        if results_sorted:
            overall_accuracy = round(sum(r['accuracy'] for r in results_sorted) / len(results_sorted), 5)
        else:
            overall_accuracy = None
        combined_results[f'top_{top_n}'] = {
            'most_recent_shows': len(results_sorted),
            'overall_accuracy': overall_accuracy,
            'results': results_sorted
        }
    save_json_path = f"{prediction_save_dir}/notebook_accuracy.json"
    with open(save_json_path, 'w') as f:
        json.dump(combined_results, f, indent=2)
    logger.info(f"Saved combined accuracy results to {save_json_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate historical prediction accuracy for both top 25 and top 50 predictions.")
    parser.add_argument("--num_shows", type=int, default=50, help="Number of shows to evaluate")
    args = parser.parse_args()
    evaluate_historical_accuracy(num_shows=args.num_shows)
    print(f"Saved results to {prediction_save_dir}/notebook_accuracy_top25.json and {prediction_save_dir}/notebook_accuracy_top50.json")
