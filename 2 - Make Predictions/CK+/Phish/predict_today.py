import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from data_loader import load_setlist_and_showdata
from model import aggregate_setlist_features
from logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../3 - Data/Phish/PhishNet"))
    setlist_path = os.path.join(data_folder, "setlistdata.csv")
    showdata_path = os.path.join(data_folder, "showdata.csv")
    songdata_path = os.path.join(data_folder, "songdata.csv")
    df = load_setlist_and_showdata(setlist_path, showdata_path, songdata_path)
    # Assign sequential show index by showdate for CK+ model (show_index_overall)
    show_order = df[['showid', 'showdate']].drop_duplicates().sort_values('showdate').reset_index(drop=True)
    show_order['show_index_overall'] = show_order.index + 1
    df = df.merge(show_order[['showid', 'show_index_overall']], on='showid', how='left')
    today = datetime.now().strftime("%Y-%m-%d")
    ckplus_df = aggregate_setlist_features(df)
    predictions_folder = os.path.abspath(os.path.join(data_folder, '../Predictions'))
    os.makedirs(predictions_folder, exist_ok=True)
    out_path = os.path.join(predictions_folder, 'todaysck+.csv')
    ckplus_df.to_csv(out_path, index=False)
    logger.info(f"Saved CK+ predictions to {out_path}")
