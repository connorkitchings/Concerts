"""
Script to run the WSP (Widespread Panic) data collection pipeline from the command line.
"""

import logging
import os
import sys

# Ensure src/jambandnerd/data_collection/wsp is on the path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
WSP_PIPELINE_DIR = os.path.join(
    ROOT_DIR, "src", "jambandnerd", "data_collection", "wsp"
)
sys.path.insert(0, WSP_PIPELINE_DIR)
sys.path.insert(0, os.path.dirname(WSP_PIPELINE_DIR))  # For shared modules

from run_pipeline import main as wsp_main  # type: ignore


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
