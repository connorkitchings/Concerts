# Orchestration script for UM scraping pipeline
import os
import sys
from datetime import datetime  # Added for timestamp formatting

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import traceback

from common_config import DATETIME_FORMAT  # Import DATETIME_FORMAT for parsing
from export_data import save_query_data, save_um_data
from logger import get_logger  # Removed restrict_to_repo_root
from scrape_setlists import fetch_um_setlist_data
from scrape_shows import create_show_data
from scrape_songs import scrape_um_songs
from scrape_venues import scrape_um_venues
from UM.config import (  # Import band-specific LOG_FILE_PATH
    DATA_COLLECTED_DIR,
    LOG_FILE_PATH,
)
from UM.utils import get_last_update_time


def main() -> None:
    """
    Orchestrates the UM scraping pipeline: scrapes song, venue, and setlist data, saves the results,
    and logs progress and errors.

    Inputs: None (uses utility functions and imported modules).
    Outputs: None (side effects: saves data to disk, logs output).
    """
    # Use the band-specific log file path from UM.config
    logger = get_logger(__name__, log_file=LOG_FILE_PATH, add_console_handler=True)
    start_time = time.time()
    try:
        data_dir = DATA_COLLECTED_DIR
        last_update_str = get_last_update_time(data_dir)
        if last_update_str:
            try:
                # Parse the existing timestamp (YYYY-MM-DD HH:MM:SS)
                dt_object = datetime.strptime(last_update_str, DATETIME_FORMAT)
                # Format to MM/DD/YYYY HH:MM
                formatted_prev_update = dt_object.strftime("%m/%d/%Y %H:%M")
                logger.info(f"Previous Last update: {formatted_prev_update}")
            except ValueError:
                # If parsing fails, log the original string as a fallback
                logger.warning(
                    f"Could not parse previous update timestamp: {last_update_str}. Logging as is."
                )
                logger.info(f"Previous Last update: {last_update_str}")
        else:
            logger.info("No previous update found.")

        # Scrape songs
        logger.info("Scraping latest song data...")
        song_data = scrape_um_songs()
        logger.info(f"Song scraping completed. Found {len(song_data)} songs.")

        # Scrape venues
        logger.info("Scraping latest venue data...")
        venue_data = scrape_um_venues()

        # Scrape setlists
        logger.info("Scraping full setlist data...")
        setlist_data = fetch_um_setlist_data()
        logger.info(
            f"Fetched {len(setlist_data):,} setlist songs for {len(setlist_data['link'].unique()):,} shows."
        )

        # Create and save showdata.csv
        create_show_data(setlist_data, data_dir)

        # Save all data
        save_um_data(song_data, venue_data, setlist_data, data_dir)
        save_query_data(data_dir)
        elapsed = time.time() - start_time
        logger.info(f"UM pipeline completed in {elapsed:.2f} seconds.")
    except Exception as e:
        logger.error(f"UM pipeline failed: {e}\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
