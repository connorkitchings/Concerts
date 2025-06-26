"""
Script to run the Goose data collection pipeline from the command line.
"""

import sys
import os
# Add the src directory to sys.path so jambandnerd imports work when running from scripts/
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
)

import logging
# IDEs may report this as unresolved, but it works at runtime due to sys.path modification above.
from jambandnerd.data_collection.goose.run_pipeline import main as goose_main


def run_goose_pipeline() -> None:
    """Run the Goose data collection pipeline and log status."""
    import os
    setlist_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'goose', 'collected', 'setlistdata.csv')
    if not os.path.exists(setlist_path):
        os.makedirs(os.path.dirname(setlist_path), exist_ok=True)
        with open(setlist_path, 'w') as f:
            f.write('show_id,date,venue,city,state\n')  # Replace with actual headers as needed
        logging.warning(f"{setlist_path} not found. Created an empty file with headers.")
    logging.info("Starting Goose pipeline...")
    try:
        goose_main()
        logging.info("Goose pipeline completed successfully.")
    except Exception as e:
        logging.exception("Goose pipeline failed: %s", e)


if __name__ == "__main__":
    run_goose_pipeline()
