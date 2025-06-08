import sys
import os
import json
from datetime import datetime # Added for timestamp formatting
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger # Removed restrict_to_repo_root
from Phish.config import API_KEY # Import API_KEY directly from config
from export_data import save_phish_data, save_query_data
from Phish.config import DATA_COLLECTED_DIR, LOG_FILE_PATH # Import band-specific LOG_FILE_PATH
from common_config import DATETIME_FORMAT # Import DATETIME_FORMAT for parsing
from loaders import load_song_data, load_show_data, load_setlist_data
import time

"""
Phish Setlist Creation Pipeline Orchestration Script

Runs the scraping, processing, and saving of Phish show, song, and setlist data.
All configuration is managed via config.py and environment variables.
"""
def main() -> None:
    import traceback
    # Use the band-specific log file path from Phish.config
    logger = get_logger(__name__, log_file=LOG_FILE_PATH, add_console_handler=True)
    api_key = API_KEY # Use API_KEY from config
    data_dir = DATA_COLLECTED_DIR
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
        try:
            # Parse the existing timestamp (assuming YYYY-MM-DD HH:MM:SS)
            dt_object = datetime.strptime(prev_update, DATETIME_FORMAT)
            # Format to MM/DD/YYYY HH:MM
            formatted_prev_update = dt_object.strftime('%m/%d/%Y %H:%M')
            logger.info(f"Previous Last update: {formatted_prev_update}")
        except ValueError:
            # If parsing fails, log the original string as a fallback
            logger.warning(f"Could not parse previous update timestamp: {prev_update}. Logging as is.")
            logger.info(f"Previous Last update: {prev_update}")
    else:
        logger.info("No previous update found.")
    start_time = time.time()
    try:
        logger.info("Loading Song Data")
        song_data = load_song_data(api_key)
        logger.info("Loading Show and Venue Data")
        show_data, venue_data = load_show_data(api_key)
        logger.info("Loading Setlist and Transition Data")
        setlist_data, transition_data = load_setlist_data(api_key, data_dir)
        logger.info(f"load_setlist_data returned. Setlist data rows: {len(setlist_data):,}, Transition data rows: {len(transition_data):,}")
        save_phish_data(song_data, show_data, venue_data, setlist_data, transition_data, data_dir)
        save_query_data(data_dir)
        elapsed = time.time() - start_time
        logger.info(f"Phish pipeline completed in {elapsed:.2f} seconds.")
    except Exception as e:
        logger.error(f"Phish pipeline failed: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()