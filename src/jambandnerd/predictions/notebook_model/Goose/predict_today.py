"""
Goose predictions script.
Handles prediction workflow for Goose band using setlist and show data.
"""

import os
from datetime import datetime

from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features
from utils.logger import get_logger, restrict_to_repo_root
import pathlib
from utils.prediction_utils import update_date_updated

logger = get_logger(__name__)

if __name__ == "__main__":
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
    today = datetime.now().strftime("%m-%d-%Y")
    agg_df = aggregate_setlist_features(df, today)
    os.makedirs(generated_folder, exist_ok=True)
    agg_df.to_csv(generated_folder / "todaysnotebook.csv", index=False)
    logger.info(f"Saved Notebook predictions to {generated_folder}")

    # Update date_updated.json after successful save
    update_date_updated("goose", "notebook", datetime.now().isoformat())
