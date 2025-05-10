# Orchestration script for UM scraping pipeline
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger
from scrape_songs import scrape_um_songs
from scrape_shows import scrape_um_shows
from scrape_setlists import load_existing_data, get_last_update_time, scrape_um_setlist_data
from save_data import save_um_data, save_query_data
from utils import get_data_dir
import argparse
import pandas as pd
import time

def main(update_setlists=True):
    import traceback
    logger = get_logger(__name__)
    start_time = time.time()
    try:
        data_dir = get_data_dir()
        existing_data = load_existing_data(data_dir)
        last_update = get_last_update_time(data_dir)
        logger.info(f"Previous Last update: {last_update}")

        # Always scrape song and venue data
        logger.info("Scraping latest song data...")
        new_song_data = scrape_um_songs()
        if not existing_data['songdata.csv'].empty:
            merged_songs = pd.concat([existing_data['songdata.csv'], new_song_data]).drop_duplicates(subset=['Song Name'])
        else:
            merged_songs = new_song_data

        logger.info("Scraping latest venue data...")
        _, new_venue_data = scrape_um_shows()
        if not existing_data['venuedata.csv'].empty:
            merged_venues = pd.concat([existing_data['venuedata.csv'], new_venue_data]).drop_duplicates()
        else:
            merged_venues = new_venue_data

        # Only update setlist data if requested
        if update_setlists:
            logger.info("Scraping latest setlist data (this may take a while)...")
            new_setlist_data = scrape_um_setlist_data()
            if not existing_data['setlistdata.csv'].empty:
                merged_setlists = pd.concat([existing_data['setlistdata.csv'], new_setlist_data]).drop_duplicates()
            else:
                merged_setlists = new_setlist_data
        else:
            logger.info("Loading existing setlist data (no update)...")
            merged_setlists = existing_data['setlistdata.csv']

        logger.info("Saving updated data...")
        save_um_data(merged_songs, merged_venues, merged_setlists, data_dir)
        save_query_data(data_dir)
        logger.info("UM data update complete.")
        elapsed = time.time() - start_time
        logger.info(f"UM pipeline completed in {elapsed:.2f} seconds.")
    except Exception as e:
        logger.error(f"UM pipeline failed: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UM Data Scraper")
    parser.add_argument('--update-setlists', action='store_true', help='Scrape and update setlist data (slow)')
    args = parser.parse_args()
    main(update_setlists=args.update_setlists)
