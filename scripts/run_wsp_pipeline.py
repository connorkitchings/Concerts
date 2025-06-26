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
    logging.info("Starting WSP pipeline...")
    try:
        wsp_main()
        logging.info("WSP pipeline completed successfully.")
    except Exception as e:
        logging.exception(f"WSP pipeline failed: {e}")


if __name__ == "__main__":
    run_wsp_pipeline()
