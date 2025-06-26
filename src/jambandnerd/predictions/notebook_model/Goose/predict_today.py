"""
Goose predictions script.
Handles prediction workflow for Goose band using setlist and show data.
"""

import os
import sys
from datetime import datetime

# Ensure parent directory is in sys.path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features
from utils.logger import get_logger, restrict_to_repo_root
from utils.prediction_utils import update_date_updated

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
    today = datetime.now().strftime("%m-%d-%Y")
    agg_df = aggregate_setlist_features(df, today)
    agg_df.to_csv(os.path.join(generated_folder, "todaysnotebook.csv"), index=False)
    logger.info(
        f"Saved Notebook predictions to {restrict_to_repo_root(generated_folder)}"
    )

    # Update date_updated.json after successful save
    update_date_updated("Goose", "Notebook", datetime.now().isoformat())
