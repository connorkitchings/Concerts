"""
predict_today.py - Goose CK+ Prediction Runner
Runs the prediction pipeline for Goose using local utils and model modules.

Recommended usage: Run this script from the CKPlus root directory, e.g.
    python -m Goose.predict_today
or ensure CKPlus is in your PYTHONPATH.
"""

import os
from datetime import datetime
import pathlib

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.logger import get_logger
from utils.prediction_utils import update_date_updated

from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features

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

    data_folder = project_root / "data" / "goose"
    collected_folder = data_folder / "collected"
    generated_folder = data_folder / "generated"
    setlist_path = collected_folder / "setlistdata.csv"
    showdata_path = collected_folder / "showdata.csv"
    songdata_path = collected_folder / "songdata.csv"
    df = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    ckplus_df = aggregate_setlist_features(df)
    os.makedirs(generated_folder, exist_ok=True)
    ckplus_df.to_csv(generated_folder / "todaysckplus.csv", index=False)
    logger.info("Saved CK+ predictions to %s", generated_folder)

    # Update date_updated.json after successful save
    update_date_updated("goose", "CK+", datetime.now().isoformat())
