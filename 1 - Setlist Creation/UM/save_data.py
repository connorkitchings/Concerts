import os
import json
from datetime import datetime
import pandas as pd
from scrape_setlists import _sort_setlist_df

def save_um_data(song_data, venue_data, setlist_data, data_dir):
    os.makedirs(data_dir, exist_ok=True)
    from datetime import date
    today = date.today()
    # Try to find the next show from venue_data if possible
    if 'Last Played' in venue_data.columns:
        # Ensure 'Last Played' is datetime.date
        venue_data['Last Played'] = pd.to_datetime(venue_data['Last Played'], errors='coerce').dt.date
        venue_data_sorted = venue_data.sort_values('Last Played')
        next_show = venue_data_sorted[venue_data_sorted['Last Played'] >= today].head(1)
    else:
        next_show = None
    next_show_path = os.path.join(data_dir, "next_show.json")
    if next_show is not None and not next_show.empty:
        next_show_record = next_show.iloc[0].to_dict()
        # Ensure all date/datetime objects are converted to strings
        for k, v in next_show_record.items():
            if hasattr(v, 'isoformat'):
                next_show_record[k] = v.isoformat()
        with open(next_show_path, "w") as f:
            json.dump({"next_show": next_show_record}, f, indent=2)
    else:
        if os.path.exists(next_show_path):
            os.remove(next_show_path)
    data_pairs = {
        'songdata.csv': song_data,
        'venuedata.csv': venue_data,
        'setlistdata.csv': _sort_setlist_df(setlist_data)
    }
    for filename, data in data_pairs.items():
        filepath = os.path.join(data_dir, filename)
        data.to_csv(filepath, index=False)

def save_query_data(data_dir):
    update_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    last_updated_path = os.path.join(data_dir, "last_updated.json")
    with open(last_updated_path, "w") as f:
        json.dump({"last_updated": update_time}, f)
