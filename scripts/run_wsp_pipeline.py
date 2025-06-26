"""
Script to run the WSP (Widespread Panic) data collection pipeline from the command line.
"""

import logging
import os
import sys

# Ensure src/jambandnerd/data_collection/wsp is on the path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.jambandnerd.data_collection.wsp.run_pipeline import (
    main as wsp_main,  # type: ignore
)


def run_wsp_pipeline() -> None:
    """Run the WSP data collection pipeline and log status."""
    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
    )
    setlist_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wsp', 'collected', 'setlistdata.csv')
    if not os.path.exists(setlist_path):
        os.makedirs(os.path.dirname(setlist_path), exist_ok=True)
        with open(setlist_path, 'w') as f:
            f.write('show_id,date,venue,city,state\n')  # Replace with actual headers as needed
        logging.warning(f"{setlist_path} not found. Created an empty file with headers.")
    logging.info("Starting WSP pipeline...")
    try:
        wsp_main()
        logging.info("WSP pipeline completed successfully.")
    except Exception as e:
        logging.exception("WSP pipeline failed: %s", e)


if __name__ == "__main__":
    run_wsp_pipeline()
