import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger
from save_data import save_goose_data, save_query_data
from utils import get_data_dir
from loaders import load_song_data, load_show_data, load_setlist_data
import time

def main():
    import traceback
    logger = get_logger(__name__)
    data_dir = get_data_dir()
    # Log previous last update
    last_updated_path = os.path.join(data_dir, "last_updated.json")
    prev_update = None
    if os.path.exists(last_updated_path):
        try:
            with open(last_updated_path, "r") as f:
                prev_update = json.load(f).get("last_updated")
        except Exception as e:
            logger.warning(f"Could not read last_updated.json: {e}")
    if prev_update:
        logger.info(f"Previous Last update: {prev_update}")
    else:
        logger.info("No previous update found.")
    start_time = time.time()
    try:
        logger.info("Loading Song Data")
        song_data = load_song_data()
        logger.info("Loading Show, Venue, and Tour Data")
        show_data, venue_data, tour_data = load_show_data()
        logger.info("Loading Setlist and Transition Data")
        setlist_data, transition_data = load_setlist_data(data_dir)
        save_goose_data(song_data, show_data, venue_data, setlist_data, transition_data, data_dir)
        save_query_data(data_dir)
        elapsed = time.time() - start_time
        logger.info(f"Goose pipeline completed in {elapsed:.2f} seconds.")
    except Exception as e:
        logger.error(f"Goose pipeline failed: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()
