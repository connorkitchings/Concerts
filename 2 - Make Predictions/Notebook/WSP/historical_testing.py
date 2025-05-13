import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from datetime import datetime
from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features
import json
import argparse

# Logger is optional, if not present, fallback to print
try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = None
    def log_info(msg): print(msg)
else:
    def log_info(msg): logger.info(msg)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../3 - Data/WSP/"))
setlist_path = os.path.join(data_folder, "EverydayCompanion/setlistdata.csv")
showdata_path = os.path.join(data_folder, "EverydayCompanion/showdata.csv")
songdata_path = os.path.join(data_folder, "EverydayCompanion/songdata.csv")
prediction_save_dir = os.path.join(data_folder, "Predictions/notebook")
os.makedirs(prediction_save_dir, exist_ok=True)

def evaluate_historical_accuracy(num_shows=50):
    """
    Evaluate prediction accuracy over the last `num_shows` shows for both top 25 and top 50 predictions.
    Saves results to a single JSON file with both groups, sorted by showdate descending.
    """
    df = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    show_dates = (
        df[['link', 'show_date']]
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
            showid = row['link']
            showdate = row['show_date']
            log_info(f"Evaluating show {showid} on {showdate.date()} for top_{top_n}")
            df_before = df[df['show_date'] < showdate]
            if df_before.empty:
                log_info(f"No data before show {showid} on {showdate.date()}, skipping.")
                continue
            agg_df = aggregate_setlist_features(df_before, showdate)
            predicted_songs = agg_df['song'].head(top_n).tolist()
            actual_songs = (
                df[df['link'] == showid]['song']
                .dropna()
                .unique()
                .tolist()
            )
            if not actual_songs:
                log_info(f"No actual setlist found for show {showid}, skipping.")
                continue
            accuracy = round(sum(1 for song in actual_songs if song in predicted_songs) / len(actual_songs), 5)
            results.append({
                'showid': str(showid),
                'showdate': str(showdate.date()),
                'accuracy': accuracy
            })
            log_info(f"Show {showid} (top_{top_n}): {sum(1 for song in actual_songs if song in predicted_songs)}/{len(actual_songs)} correct ({accuracy:.2%})")
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
    save_json_path = os.path.join(prediction_save_dir, "notebook_accuracy.json")
    with open(save_json_path, 'w') as f:
        json.dump(combined_results, f, indent=2)
    log_info(f"Saved combined accuracy results to {save_json_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate historical prediction accuracy for both top 25 and top 50 predictions.")
    parser.add_argument("--num_shows", type=int, default=50, help="Number of shows to evaluate")
    args = parser.parse_args()
    evaluate_historical_accuracy(num_shows=args.num_shows)
    print(f"Saved results to {os.path.join(prediction_save_dir, 'notebook_accuracy.json')}")
