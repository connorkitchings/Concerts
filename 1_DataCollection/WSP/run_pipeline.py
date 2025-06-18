"""
WSP Setlist Creation Pipeline Orchestration Script

Runs the scraping, processing, and saving of Widespread Panic (WSP) show, song, and setlist data.
All configuration is managed via config.py and environment variables.
"""

import json  # Moved import json to top
import os
import sys
from datetime import datetime  # Added for timestamp formatting

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import time

import pandas as pd
from common_config import DATETIME_FORMAT  # Import DATETIME_FORMAT for parsing
from export_data import save_wsp_data
from logger import get_logger  # Removed restrict_to_repo_root
from scrape_setlists import load_setlist_data
from scrape_shows import scrape_wsp_shows
from scrape_songs import scrape_wsp_songs
from WSP.config import (  # Import band-specific LOG_FILE_PATH
    DATA_COLLECTED_DIR,
    LOG_FILE_PATH,
)


def main() -> None:
    import traceback

    # Use the band-specific log file path from WSP.config
    logger = get_logger(__name__, log_file=LOG_FILE_PATH, add_console_handler=True)
    # Log previous last update
    data_dir = DATA_COLLECTED_DIR
    last_updated_path = os.path.join(data_dir, "last_updated.json")
    prev_update_str = None
    if os.path.exists(last_updated_path):
        try:
            with open(last_updated_path, "r") as f:
                prev_update_str = json.load(f).get("last_updated")
        except Exception as e:
            logger.warning(f"Could not read last_updated.json: {e}")

    if prev_update_str:
        try:
            # Parse the existing timestamp (YYYY-MM-DD HH:MM:SS)
            dt_object = datetime.strptime(prev_update_str, DATETIME_FORMAT)
            # Format to MM/DD/YYYY HH:MM
            formatted_prev_update = dt_object.strftime("%m/%d/%Y %H:%M")
            logger.info(f"Previous Last update: {formatted_prev_update}")
        except ValueError:
            # If parsing fails, log the original string as a fallback
            logger.warning(
                f"Could not parse previous update timestamp: {prev_update_str}. Logging as is."
            )
            logger.info(f"Previous Last update: {prev_update_str}")
    else:
        logger.info("No previous update found.")
    start_time = time.time()
    try:
        data_dir = DATA_COLLECTED_DIR
        logger.info("Scraping WSP show data...")
        show_data = scrape_wsp_shows()
        logger.info(f"Scraped {len(show_data):,} shows.")

        logger.info("Scraping WSP song catalog...")
        song_data = scrape_wsp_songs()
        logger.info(f"Scraped {len(song_data):,} songs.")

        logger.info("Scraping WSP setlists...")
        setlistdata_path = os.path.join(data_dir, "setlistdata.csv")
        existing_setlist_data = None  # Initialize here
        if os.path.exists(setlistdata_path):
            try:
                existing_setlist_data = pd.read_csv(setlistdata_path)
            except Exception as e:
                logger.warning(f"Could not load existing setlistdata.csv: {e}")
        link_list = show_data["link"].tolist()
        if len(link_list) == 0:
            logger.info("No setlist data to scrape.")
        else:
            setlist_data = load_setlist_data(
                link_list, method="update", existing_setlist_data=existing_setlist_data
            )
            logger.info(
                f"Scraped/updated setlist data for all years now has {len(setlist_data):,} rows."
            )

        logger.info("Saving WSP data...")
        save_wsp_data(song_data, show_data, setlist_data, data_dir)
        elapsed = time.time() - start_time
        logger.info(f"WSP scraping pipeline completed in {elapsed:.2f} seconds.")
    except Exception as e:
        logger.error(f"WSP pipeline failed: {e}\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
