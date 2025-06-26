"""
CLI runner for the Phish data collection pipeline. Handles sys.path for IDE/runtime compatibility.
"""

import os
import sys

# Add src to sys.path for IDE and CLI compatibility
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from jambandnerd.data_collection.phish.run_pipeline import main as phish_main


def run_phish_pipeline():
    """
    CLI entry point for running the Phish data collection pipeline.
    Calls the main() function from run_pipeline.py.
    """
    import os
    setlist_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'phish', 'collected', 'setlistdata.csv')
    if not os.path.exists(setlist_path):
        os.makedirs(os.path.dirname(setlist_path), exist_ok=True)
        with open(setlist_path, 'w') as f:
            f.write('show_id,date,venue,city,state\n')  # Replace with actual headers as needed
        print(f"WARNING: {setlist_path} not found. Created an empty file with headers.")
    print("Starting Phish pipeline...")
    try:
        success = phish_main()
        if success:
            print("Phish pipeline completed successfully.")
        else:
            print("Phish pipeline failed. See logs for details.")
            sys.exit(1)
    except Exception as e:
        # Broad exception catching is intentional for CLI robustness
        print(f"Phish pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_phish_pipeline()
