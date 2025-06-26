"""
Main script for running CK+ predictions for Phish setlists.
Loads data, computes features, saves predictions, and updates metadata.
"""

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features
from utils.logger import get_logger
from utils.prediction_utils import update_date_updated  # local to ckplus_model

logger = get_logger(__name__)

if __name__ == "__main__":
    # Robustly find project root (parent of 'src')
    script_dir = pathlib.Path(__file__).resolve().parent
    for parent in script_dir.parents:
        if parent.name == "src":
            project_root = parent.parent
            break
    else:
        project_root = script_dir.parents[3]  # fallback if 'src' not found

    data_folder = project_root / "data" / "phish"
    collected_folder = data_folder / "collected"
    generated_folder = data_folder / "generated"
    setlist_path = collected_folder / "setlistdata.csv"
    showdata_path = collected_folder / "showdata.csv"
    songdata_path = collected_folder / "songdata.csv"
    df = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    # Assign sequential show index by showdate for CK+ model (show_index_overall)
    show_order = (
        df[["showid", "showdate"]]
        .drop_duplicates()
        .sort_values("showdate")
        .reset_index(drop=True)
    )
    show_order["show_index_overall"] = show_order.index + 1
    df = df.merge(show_order[["showid", "show_index_overall"]], on="showid", how="left")
    ckplus_df = aggregate_setlist_features(df)
    generated_folder.mkdir(parents=True, exist_ok=True)
    ckplus_df.to_csv(generated_folder / "todaysckplus.csv", index=False)
    logger.info(f"Saved CK+ predictions to {generated_folder}")

    # Update date_updated.json after successful save
    update_date_updated("phish", "CK+", datetime.now().isoformat())
