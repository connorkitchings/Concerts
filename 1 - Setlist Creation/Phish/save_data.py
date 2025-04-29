import os
import json
from datetime import datetime
from utils import get_date_and_time

def save_phish_data(song_data, show_data, venue_data, setlist_data, transition_data, data_dir):
    os.makedirs(data_dir, exist_ok=True)
    # Save next upcoming show to next_show.json
    today = datetime.today().strftime('%Y-%m-%d')
    next_show = show_data[show_data['showdate'] >= today].sort_values('showdate').head(1)
    next_show_path = os.path.join(data_dir, "next_show.json")
    if not next_show.empty:
        next_show_record = next_show.iloc[0].to_dict()
        with open(next_show_path, "w") as f:
            json.dump({"next_show": next_show_record}, f, indent=2)
    else:
        if os.path.exists(next_show_path):
            os.remove(next_show_path)
    # Save all CSVs
    data_pairs = {
        'songdata.csv': song_data,
        'showdata.csv': show_data,
        'venuedata.csv': venue_data,
        'setlistdata.csv': setlist_data,
        'transitiondata.csv': transition_data
    }
    for filename, data in data_pairs.items():
        filepath = os.path.join(data_dir, filename)
        data.to_csv(filepath, index=False)
        
def save_query_data(data_dir):
    update_time = get_date_and_time()
    last_updated_path = os.path.join(data_dir, "last_updated.json")
    with open(last_updated_path, "w") as f:
        json.dump({"last_updated": update_time}, f)
