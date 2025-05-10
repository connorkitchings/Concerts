# Orchestration script for UM scraping pipeline
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger
from scrape_songs import scrape_um_songs
from scrape_shows import scrape_um_shows
from scrape_setlists import (
    scrape_um_setlist_data,
    full_um_setlist_update,
    incremental_um_setlist_update,
    get_last_update_time,
)
from save_data import save_um_data, save_query_data
from utils import get_data_dir
import time
from logger import get_logger

def main():
    import traceback
    logger = get_logger(__name__)
    start_time = time.time()
    try:
        data_dir = get_data_dir()
        last_update = get_last_update_time(data_dir)
        logger.info(f"Previous Last update: {last_update}")

        # Scrape songs
        logger.info("Scraping latest song data...")
        song_data = scrape_um_songs()

        # Scrape venues
        logger.info("Scraping latest venue data...")
        _, venue_data = scrape_um_shows()
        
        # Scrape setlists (FULL)
        #logger.info("Scraping latest setlist data...")
        #setlist_data = full_um_setlist_update()

        # Update setlists (INCREMENTAL)
        logger.info("Performing INCREMENTAL setlist update (last year + this year)...")
        setlist_data = incremental_um_setlist_update()

        # Save all data
        save_um_data(song_data, venue_data, setlist_data, data_dir)
        save_query_data(data_dir)
        logger.info("UM data update complete.")
        elapsed = time.time() - start_time
        logger.info(f"UM pipeline completed in {elapsed:.2f} seconds.")
    except Exception as e:
        logger.error(f"UM pipeline failed: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()
