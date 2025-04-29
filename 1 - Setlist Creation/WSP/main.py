# Orchestration script for WSP scraping pipeline
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from scrape_shows import scrape_wsp_shows
from scrape_songs import scrape_wsp_songs
from scrape_setlists import load_setlist_data
from save_data import save_wsp_data
from utils import get_data_dir
import pandas as pd
import os
import time

if __name__ == "__main__":
    import traceback
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    start_time = time.time()
    try:
        data_dir = get_data_dir()
        logger.info("Scraping WSP show data...")
        show_data = scrape_wsp_shows()
        logger.info(f"Scraped {len(show_data):,} shows.")

        logger.info("Scraping WSP song catalog...")
        song_data = scrape_wsp_songs()
        logger.info(f"Scraped {len(song_data):,} songs.")

        logger.info("Scraping WSP setlists (all mode)")
        setlistdata_path = os.path.join(data_dir, 'setlistdata.csv')
        if os.path.exists(setlistdata_path):
            try:
                existing_setlist_data = pd.read_csv(setlistdata_path)
                logger.info(f"Loaded existing setlistdata.csv with {len(existing_setlist_data):,} rows.")
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
