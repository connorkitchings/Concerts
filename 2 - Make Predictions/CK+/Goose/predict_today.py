import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # for logger.py in CK+
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))  # for prediction_utils
from pathlib import Path
from logger import get_logger, restrict_to_repo_root
from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features
from prediction_utils import update_date_updated

logger = get_logger(__name__)

if __name__ == "__main__":
    SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    data_folder = SCRIPT_DIR.parent.parent.parent / "3 - Data/Goose/ElGoose"
    setlist_path = data_folder / "setlistdata.csv"
    showdata_path = data_folder / "showdata.csv"
    songdata_path = data_folder / "songdata.csv"
    df = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    ckplus_df = aggregate_setlist_features(df)
    out_path = SCRIPT_DIR.parent.parent.parent / "3 - Data/Goose/Predictions/todaysck+.csv"
    ckplus_df.to_csv(out_path, index=False)
    logger.info(f"Saved CK+ predictions to {restrict_to_repo_root(out_path)}")

    # Update date_updated.json after successful save
    update_date_updated('Goose', 'CK+', '2025-05-25T11:47:37-04:00')
