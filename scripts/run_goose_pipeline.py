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
    print("Starting Goose pipeline...")
    try:
        goose_main()
        print("Goose pipeline completed successfully.")
    except Exception as e:
        # Intentionally broad Exception catch for CLI robustness; logs all errors for debugging
        # This is intentional to ensure all errors are logged and surfaced in CLI usage.
        logging.exception("Goose pipeline failed: %s", e)


if __name__ == "__main__":
    run_goose_pipeline()
