"""
Main script for running CK+ predictions for Phish setlists.
Loads data, computes features, saves predictions, and updates metadata.
"""

import os
from datetime import datetime

from predictions.ckplus.phish.data_loader import load_setlist_and_showdata
from predictions.ckplus.phish.model import aggregate_setlist_features
from predictions.ckplus.utils.logger import get_logger, restrict_to_repo_root
from predictions.ckplus.utils.prediction_utils import update_date_updated

logger = get_logger(__name__)

if __name__ == "__main__":
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    data_folder = os.path.join(root_dir, "storage/phish/")
    collected_folder = os.path.join(data_folder, "collected")
    generated_folder = os.path.join(data_folder, "generated")
    meta_folder = os.path.join(data_folder, "meta")
    setlist_path = os.path.join(collected_folder, "setlistdata.csv")
    showdata_path = os.path.join(collected_folder, "showdata.csv")
    songdata_path = os.path.join(collected_folder, "songdata.csv")
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
    ckplus_df.to_csv(os.path.join(generated_folder, "todaysckplus.csv"), index=False)
    logger.info("Saved CK+ predictions to %s", restrict_to_repo_root(generated_folder))

    # Update date_updated.json after successful save
    update_date_updated("Phish", "CK+", datetime.now().isoformat())
