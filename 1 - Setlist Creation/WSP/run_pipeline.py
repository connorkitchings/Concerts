"""
WSP Setlist Creation Pipeline Orchestration Script

Runs the scraping, processing, and saving of Widespread Panic (WSP) show, song, and setlist data.
All configuration is managed via config.py and environment variables.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger, restrict_to_repo_root
from scrape_shows import scrape_wsp_shows
from scrape_songs import scrape_wsp_songs
from scrape_setlists import load_setlist_data
from export_data import save_wsp_data
from WSP.config import DATA_DIR
from WSP.utils import get_date_and_time
import pandas as pd
import os
import time

if __name__ == "__main__":
    import traceback
    logger = get_logger(__name__, add_console_handler=True)
    # Log previous last update
    data_dir = DATA_DIR
    last_updated_path = os.path.join(data_dir, "last_updated.json")
    prev_update = None
    if os.path.exists(last_updated_path):
        try:
            import json
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
        data_dir = DATA_DIR
        logger.info("Scraping WSP show data...")
        show_data = scrape_wsp_shows()
        logger.info(f"Scraped {len(show_data):,} shows.")

        logger.info("Scraping WSP song catalog...")
        song_data = scrape_wsp_songs()
        logger.info(f"Scraped {len(song_data):,} songs.")

        logger.info("Scraping WSP setlists...")
        setlistdata_path = os.path.join(data_dir, 'setlistdata.csv')
        if os.path.exists(setlistdata_path):
            try:
                existing_setlist_data = pd.read_csv(setlistdata_path)
            except Exception as e:
                logger.warning(f"Could not load existing setlistdata.csv: {e}")
        link_list = show_data['link'].tolist()
        if len(link_list) == 0:
            logger.info("No setlist data to scrape.")
        else:
            setlist_data = load_setlist_data(link_list, method='update', existing_setlist_data=existing_setlist_data)
            logger.info(f"Scraped/updated setlist data for all years now has {len(setlist_data):,} rows.")

        logger.info("Saving WSP data...")
        save_wsp_data(song_data, show_data, setlist_data, data_dir)
        elapsed = time.time() - start_time
        logger.info(f"WSP scraping pipeline completed in {elapsed:.2f} seconds.")
    except Exception as e:
        logger.error(f"WSP pipeline failed: {e}\n{traceback.format_exc()}")
