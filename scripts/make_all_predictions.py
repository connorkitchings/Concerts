"""
update_predictions.py

Runs both CK+ and Notebook prediction pipelines for all bands in sequence.

Usage:
    python update_predictions.py
"""

import sys
from pathlib import Path
from subprocess import CalledProcessError, run

import sys
import subprocess
from pathlib import Path

def main():
    """Run all band prediction scripts (CK+ and Notebook for each band)."""
    script_path = Path(__file__).parent / "run_all_predict_todays.py"
    if not script_path.exists():
        print(f"ERROR: {script_path} does not exist.")
        sys.exit(1)
    print(f"\n=== Running all band predictions using {script_path} ===")
    try:
        result = subprocess.run([sys.executable, str(script_path)], check=True, capture_output=True, text=True)
        print(result.stdout)
        print("All prediction pipelines completed.")
    except subprocess.CalledProcessError as e:
        print(f"Error running predictions: {e}\n{e.stdout}\n{e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    main()
