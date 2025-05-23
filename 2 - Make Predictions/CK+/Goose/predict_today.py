from pathlib import Path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger
from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features

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
    logger.info(f"Saved CK+ predictions to {out_path}")
