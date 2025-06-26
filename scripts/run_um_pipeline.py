"""
Script to run the UM (Umphrey's McGee) data collection pipeline from the command line.
"""

import logging
import os
import sys

# Ensure src/jambandnerd/data_collection/um is on the path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.jambandnerd.data_collection.um.run_pipeline import main as um_main


def run_um_pipeline() -> None:
    """Run the UM data collection pipeline and log status."""
    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
    )
    # Check for setlistdata.csv before running pipeline
    setlist_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'um', 'collected', 'setlistdata.csv')
    if not os.path.exists(setlist_path):
        os.makedirs(os.path.dirname(setlist_path), exist_ok=True)
        with open(setlist_path, 'w') as f:
            f.write('show_id,date,venue,city,state\n')  # Replace with actual headers as needed
        logging.warning(f"{setlist_path} not found. Created an empty file with headers.")
    logging.info("Starting UM pipeline...")
    try:
        um_main()
        logging.info("UM pipeline completed successfully.")
    except Exception as e:
        logging.exception("UM pipeline failed: %s", e)


if __name__ == "__main__":
    run_um_pipeline()
