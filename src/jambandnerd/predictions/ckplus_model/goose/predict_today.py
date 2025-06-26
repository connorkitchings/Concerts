"""
predict_today.py - Goose CK+ Prediction Runner
Runs the prediction pipeline for Goose using local utils and model modules.

Recommended usage: Run this script from the CKPlus root directory, e.g.
    python -m Goose.predict_today
or ensure CKPlus is in your PYTHONPATH.
"""

import os
from datetime import datetime

from predictions.ckplus.goose.data_loader import load_setlist_and_showdata
from predictions.ckplus.goose.model import aggregate_setlist_features
from predictions.ckplus.utils.logger import get_logger, restrict_to_repo_root
from predictions.ckplus.utils.prediction_utils import update_date_updated

logger = get_logger(__name__)

if __name__ == "__main__":
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    data_folder = os.path.join(root_dir, "storage/goose/")
    collected_folder = os.path.join(data_folder, "collected")
    generated_folder = os.path.join(data_folder, "generated")
    meta_folder = os.path.join(data_folder, "meta")
    setlist_path = os.path.join(collected_folder, "setlistdata.csv")
    showdata_path = os.path.join(collected_folder, "showdata.csv")
    songdata_path = os.path.join(collected_folder, "songdata.csv")
    df = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    ckplus_df = aggregate_setlist_features(df)
    ckplus_df.to_csv(os.path.join(generated_folder, "todaysckplus.csv"), index=False)
    logger.info("Saved CK+ predictions to %s", restrict_to_repo_root(generated_folder))

    # Update date_updated.json after successful save
    update_date_updated("Goose", "CK+", datetime.now().isoformat())
