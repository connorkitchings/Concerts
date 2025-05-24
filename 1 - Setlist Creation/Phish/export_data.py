import os
import json
from datetime import datetime
from Phish.config import DATA_DIR, SONG_DATA_FILENAME, SHOW_DATA_FILENAME, VENUE_DATA_FILENAME, SETLIST_DATA_FILENAME, TRANSITION_DATA_FILENAME, NEXT_SHOW_FILENAME, LAST_UPDATED_FILENAME
from Phish.utils import get_date_and_time

def save_phish_data(song_data: 'pd.DataFrame', show_data: 'pd.DataFrame', venue_data: 'pd.DataFrame', setlist_data: 'pd.DataFrame', transition_data: 'pd.DataFrame', data_dir: str = DATA_DIR) -> None:
    """
    Save Phish data (songs, shows, venues, setlists, transitions) to CSV files and update JSON files for last updated and next show.

    Args:
        song_data (pd.DataFrame): DataFrame of song data.
        show_data (pd.DataFrame): DataFrame of show data.
        venue_data (pd.DataFrame): DataFrame of venue data.
        setlist_data (pd.DataFrame): DataFrame of setlist data.
        transition_data (pd.DataFrame): DataFrame of transition data.
        data_dir (str): Directory to save files. Defaults to DATA_DIR from config.
    Returns:
        None
    """
    os.makedirs(data_dir, exist_ok=True)
    # Save next upcoming show to next_show.json
    today = datetime.today().strftime('%Y-%m-%d')
    next_show = show_data[show_data['showdate'] >= today].sort_values('showdate').head(1)
    next_show_path = os.path.join(data_dir, NEXT_SHOW_FILENAME)
    if not next_show.empty:
        next_show_record = next_show.iloc[0].to_dict()
        with open(next_show_path, "w") as f:
            json.dump({"next_show": next_show_record}, f, indent=2)
    else:
        if os.path.exists(next_show_path):
            os.remove(next_show_path)
    # Save all CSVs
    data_pairs = {
        SONG_DATA_FILENAME: song_data,
        SHOW_DATA_FILENAME: show_data,
        VENUE_DATA_FILENAME: venue_data,
        SETLIST_DATA_FILENAME: setlist_data,
        TRANSITION_DATA_FILENAME: transition_data
    }
    for filename, data in data_pairs.items():
        filepath = os.path.join(data_dir, filename)
        data.to_csv(filepath, index=False)
        
def save_query_data(data_dir: str = DATA_DIR) -> None:
    """
    Save the last updated timestamp to a JSON file.

    Args:
        data_dir (str): Directory to save the file. Defaults to DATA_DIR from config.
    Returns:
        None
    """
    update_time = get_date_and_time()
    last_updated_path = os.path.join(data_dir, LAST_UPDATED_FILENAME)
    with open(last_updated_path, "w") as f:
        json.dump({"last_updated": update_time}, f)
