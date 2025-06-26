"""
Run CK+ prediction pipeline for UM.
Loads data, generates predictions, and saves outputs for today's show.
"""

import os
from datetime import datetime

from predictions.ckplus.um.data_loader import load_setlist_and_showdata
from predictions.ckplus.um.model import aggregate_setlist_features
from predictions.ckplus.utils.logger import get_logger, restrict_to_repo_root
from predictions.ckplus.utils.prediction_utils import update_date_updated

logger = get_logger(__name__)

if __name__ == "__main__":
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    data_folder = os.path.join(root_dir, "storage/um/")
    collected_folder = os.path.join(data_folder, "collected")
    generated_folder = os.path.join(data_folder, "generated")
    meta_folder = os.path.join(data_folder, "meta")
    setlist_path = os.path.join(collected_folder, "setlistdata.csv")
    venuedata_path = os.path.join(collected_folder, "venuedata.csv")
    songdata_path = os.path.join(collected_folder, "songdata.csv")
    df = load_setlist_and_showdata(setlist_path, venuedata_path, songdata_path)
    ckplus_df = aggregate_setlist_features(df)
    ckplus_df.to_csv(os.path.join(generated_folder, "todaysckplus.csv"), index=False)
    logger.info("Saved CK+ predictions to %s", restrict_to_repo_root(generated_folder))

    # Update date_updated.json after successful save
    update_date_updated("UM", "CK+", datetime.now().isoformat())
