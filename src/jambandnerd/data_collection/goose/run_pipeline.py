"""
Goose Setlist Creation Pipeline Orchestration Script.
Runs the scraping, processing, and saving of Goose show, song, and setlist data.
All configuration is managed via config.py and environment variables.
"""

import json
import os
import time
import traceback

from .export_data import save_goose_data, save_query_data
from .loaders import load_setlist_data, load_show_data, load_song_data
from .utils import get_logger


def main() -> None:
    """
    Orchestrate the Goose data collection pipeline: load, process, and save all data.
    """
    # Ensure logs/Goose/ is always relative to the project root, not src/
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    )
    logs_dir = os.path.join(project_root, "logs", "Goose")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "goose_pipeline.log")
    logger = get_logger(__name__, log_file=log_file)
    data_dir = "data/goose/collected"
    # Log previous last update
    last_updated_path = os.path.join(data_dir, "last_updated.json")
    prev_update = None
    if os.path.exists(last_updated_path):
        try:
            with open(last_updated_path, encoding="utf-8") as f:
                prev_update = json.load(f).get("last_updated")
        # Intentionally broad Exception catch to ensure pipeline continues
        # if last_updated.json is corrupt or missing
        except Exception as e:
            logger.warning("Could not read last_updated.json: %s", e)
    if prev_update:
        logger.info("Previous Last update: %s", prev_update)
    else:
        logger.info("No previous update found.")
    start_time = time.time()
    try:
        logger.info("Loading Song Data")
        song_data = load_song_data()
        logger.info("Loading Show, Venue, and Tour Data")
        show_data, venue_data, _ = load_show_data()
        logger.info("Loading Setlist and Transition Data")
        setlist_data, transition_data = load_setlist_data()
        save_goose_data(
            song_data, show_data, venue_data, setlist_data, transition_data, data_dir
        )
        save_query_data(data_dir)
        elapsed = time.time() - start_time
        logger.info("Goose pipeline completed in %.2f seconds.", elapsed)
    # Intentionally broad Exception catch for pipeline robustness; logs all errors for debuggin
    except Exception as e:
        logger.error("Goose pipeline failed: %s\n%s", e, traceback.format_exc())


if __name__ == "__main__":
    main()
