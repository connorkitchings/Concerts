# Orchestration script for UM scraping pipeline
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger
from scrape_songs import scrape_um_songs
from scrape_shows import scrape_um_shows
from scrape_setlists import fetch_um_setlist_data
from save_data import save_um_data, save_query_data
from utils import get_data_dir, get_last_update_time
import time
import traceback


def main():
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
        venue_data = scrape_um_shows()
        
        # Scrape setlists
        logger.info("Scraping full setlist data...")
        setlist_data = fetch_um_setlist_data()
        logger.info(f"Fetched {len(setlist_data):,} setlist songs for {len(setlist_data['link'].unique()):,} shows.")

        # Save all data
        save_um_data(song_data, venue_data, setlist_data, data_dir)
        save_query_data(data_dir)
        elapsed = time.time() - start_time
        logger.info(f"UM pipeline completed in {elapsed:.2f} seconds.")
    except Exception as e:
        logger.error(f"UM pipeline failed: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()
