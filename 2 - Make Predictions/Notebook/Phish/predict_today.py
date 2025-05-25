import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features
from logger import get_logger, restrict_to_repo_root

logger = get_logger(__name__)

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../3 - Data/Phish/"))
    setlist_path = os.path.join(data_folder, "PhishNet/setlistdata.csv")
    showdata_path = os.path.join(data_folder, "PhishNet/showdata.csv")
    songdata_path = os.path.join(data_folder, "PhishNet/songdata.csv")
    df = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    today = datetime.now().strftime("%m-%d-%Y")
    agg_df = aggregate_setlist_features(df, today)
    out_path = os.path.join(data_folder, "Predictions/todaysnotebook.csv")
    agg_df.to_csv(out_path, index=False)
    logger.info(f"Saved Notebook predictions to {restrict_to_repo_root(out_path)}")
