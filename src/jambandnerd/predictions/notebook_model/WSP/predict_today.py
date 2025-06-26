import os
from datetime import datetime
import pathlib

from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import get_logger, restrict_to_repo_root
from utils.prediction_utils import update_date_updated

logger = get_logger(__name__)

if __name__ == "__main__":
    script_dir = pathlib.Path(__file__).resolve().parent
    for parent in script_dir.parents:
        if parent.name == "src":
            project_root = parent.parent
            break
    else:
        project_root = script_dir.parents[3]
    data_folder = project_root / "data" / "WSP"
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
    logger.info(
        f"Saved Notebook predictions to {restrict_to_repo_root(str(generated_folder))}"
    )
    update_date_updated("WSP", "Notebook", datetime.now().isoformat())
