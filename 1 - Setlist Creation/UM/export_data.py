from UM.config import DATA_DIR, SONG_DATA_FILENAME, VENUE_DATA_FILENAME, SETLIST_DATA_FILENAME, NEXT_SHOW_FILENAME, LAST_UPDATED_FILENAME
from datetime import datetime, date
import pandas as pd
import json
from pathlib import Path
from logger import get_logger
logger = get_logger(__name__, add_console_handler=True)

def save_um_data(song_data: pd.DataFrame, venue_data: pd.DataFrame, setlist_data: pd.DataFrame, data_dir=None) -> None:
    data_dir = Path(data_dir) if data_dir is not None else Path(DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    today = date.today()
    if 'Last Played' in venue_data.columns:
        venue_data['Last Played'] = pd.to_datetime(venue_data['Last Played'], errors='coerce').dt.date
        venue_data_sorted = venue_data.sort_values('Last Played')
        next_show = venue_data_sorted[venue_data_sorted['Last Played'] >= today].head(1)
    else:
        next_show = None
    next_show_path = data_dir / NEXT_SHOW_FILENAME
    if next_show is not None and not next_show.empty:
        next_show_record = next_show.iloc[0].to_dict()
        for k, v in next_show_record.items():
            if hasattr(v, 'isoformat'):
                next_show_record[k] = v.isoformat()
        with open(next_show_path, "w") as f:
            json.dump({"next_show": next_show_record}, f, indent=2)
    else:
        if next_show_path.exists():
            next_show_path.unlink()
    song_data.to_csv(data_dir / SONG_DATA_FILENAME, index=False)
    venue_data.to_csv(data_dir / VENUE_DATA_FILENAME, index=False)
    setlist_data.to_csv(data_dir / SETLIST_DATA_FILENAME, index=False)

def save_query_data(data_dir=None) -> None:
    data_dir = Path(data_dir) if data_dir is not None else Path(DATA_DIR)
    update_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    last_updated_path = data_dir / LAST_UPDATED_FILENAME
    with open(last_updated_path, "w") as f:
        json.dump({"last_updated": update_time}, f)
