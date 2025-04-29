import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger
from call_api import access_credentials
from save_data import save_phish_data, save_query_data
from utils import get_data_dir
from loaders import load_song_data, load_show_data, load_setlist_data
import time

def main():
    import traceback
    logger = get_logger(__name__)
    api_key = access_credentials()
    data_dir = get_data_dir()
    start_time = time.time()
    try:
        logger.info("Loading Song Data")
        song_data = load_song_data(api_key)
        logger.info("Loading Show and Venue Data")
        show_data, venue_data = load_show_data(api_key)
        logger.info("Loading Setlist and Transition Data")
        setlist_data, transition_data = load_setlist_data(api_key, data_dir)
        save_phish_data(song_data, show_data, venue_data, setlist_data, transition_data, data_dir)
        save_query_data(data_dir)
        elapsed = time.time() - start_time
        logger.info(f"Phish pipeline completed in {elapsed:.2f} seconds.")
    except Exception as e:
        logger.error(f"Phish pipeline failed: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()