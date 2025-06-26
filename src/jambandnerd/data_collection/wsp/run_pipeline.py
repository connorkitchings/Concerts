"""
WSP Setlist Creation Pipeline Orchestration Script

Runs the scraping, processing, and saving of Widespread Panic (WSP) show, song, and setlist data.
All configuration is managed via config.py and environment variables.
"""

import json  # Moved import json to top
import os
import sys
import time
from datetime import datetime

import pandas as pd

try:
    from jambandnerd.data_collection.wsp.export_data import save_wsp_data
    from jambandnerd.data_collection.wsp.scrape_setlists import load_setlist_data
    from jambandnerd.data_collection.wsp.scrape_shows import scrape_wsp_shows
    from jambandnerd.data_collection.wsp.scrape_songs import scrape_wsp_songs
    from jambandnerd.data_collection.wsp.utils import get_logger
except ImportError:
    from export_data import save_wsp_data
    from scrape_setlists import load_setlist_data
    from scrape_shows import scrape_wsp_shows
    from scrape_songs import scrape_wsp_songs
    from utils import get_logger

# Inlined constants
DATA_COLLECTED_DIR = "data/wsp/collected"
LOG_FILE_PATH = "logs/wsp/wsp_pipeline.log"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
BAND_NAME = "WSP"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = get_logger(__name__, log_file=LOG_FILE_PATH, add_console_handler=True)


def main():
    """Run the WSP data collection pipeline."""

    # Log previous last update
    data_dir = DATA_COLLECTED_DIR
    last_updated_path = os.path.join(data_dir, "last_updated.json")
    prev_update_str = None
    if os.path.exists(last_updated_path):
        try:
            with open(last_updated_path, encoding="utf-8") as f:
                prev_update_str = json.load(f).get("last_updated")
        except (FileNotFoundError, OSError, json.JSONDecodeError) as e:
            logger.error("Failed to load last update: %s", e)
    if prev_update_str:
        try:
            # Parse the existing timestamp (YYYY-MM-DD HH:MM:SS)
            dt_object = datetime.strptime(prev_update_str, DATETIME_FORMAT)
            # Format to MM/DD/YYYY HH:MM
            formatted_prev_update = dt_object.strftime("%m/%d/%Y %H:%M")
            logger.info("Previous Last update: %s", formatted_prev_update)
        except ValueError:
            # If parsing fails, log the original string as a fallback
            logger.warning(
                "Could not parse previous update timestamp: %s. Logging as is.",
                prev_update_str,
            )
            logger.info("Previous Last update: %s", prev_update_str)
    else:
        logger.info("No previous update found.")
    start_time = time.time()
    try:
        data_dir = DATA_COLLECTED_DIR
        logger.info("Scraping WSP show data...")
        show_data = scrape_wsp_shows()
        logger.info("Scraped %d shows.", len(show_data))

        logger.info("Scraping WSP song catalog...")
        song_data = scrape_wsp_songs()
        logger.info("Scraped %d songs.", len(song_data))

        logger.info("Scraping WSP setlists...")
        setlistdata_path = os.path.join(data_dir, "setlistdata.csv")
        existing_setlist_data = None  # Initialize here
        if os.path.exists(setlistdata_path):
            try:
                existing_setlist_data = pd.read_csv(setlistdata_path)
            except Exception as e:
                logger.warning("Could not load existing setlistdata.csv: %s", e)
        link_list = show_data["link"].tolist()
        if len(link_list) == 0:
            logger.info("No setlist data to scrape.")
        else:
            setlist_data = load_setlist_data(
                link_list, method="update", existing_setlist_data=existing_setlist_data
            )
            logger.info(
                "Scraped/updated setlist data for all years now has %d rows.",
                len(setlist_data),
            )

        logger.info("Saving WSP data...")
        save_wsp_data(song_data, show_data, setlist_data, data_dir)
        elapsed = time.time() - start_time
        logger.info("WSP scraping pipeline completed in %.2f seconds.", elapsed)
    except Exception as e:
        logger.exception("WSP pipeline failed: %s", e)


if __name__ == "__main__":
    main()
