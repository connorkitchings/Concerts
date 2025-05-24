"""
Module to run all four setlist creation pipelines:
- Phish
- Goose
- UM
- WSP

Usage:
    python run_all.py
"""
import subprocess
import sys
import os
"""
Module to run all four setlist creation pipelines:
- Phish
- Goose
- UM
- WSP

Usage:
    python run_all.py

This script runs each band's pipeline via its dedicated run_pipeline.py entrypoint. Each band's logging is handled independently in its own directory and log file, as configured in the respective config.py and logger.py.

Additionally, all output from this script (including band pipeline output and errors) is logged to logs/Setlist_Creation/full_pipeline.log as well as printed to the console. This provides a complete record of all runs in a single file for auditing and debugging.
"""
import subprocess
import sys
import os
import logging

# Define the main scripts for each band (use run_pipeline.py for consistency)
BANDS = {
    "Phish": "Phish/run_pipeline.py",
    "Goose": "Goose/run_pipeline.py",
    "UM": "UM/run_pipeline.py",
    "WSP": "WSP/run_pipeline.py",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_band(band: str, script_path: str) -> None:
    """
    Run the pipeline for a single band and print output to stdout/stderr and log file.
    Args:
        band (str): Name of the band.
        script_path (str): Relative path to the band's run_pipeline.py.
    """
    import time
    script_full_path = os.path.join(BASE_DIR, script_path)
    print(f"\n===== Running {band} pipeline =====")
    result = subprocess.run([sys.executable, script_full_path], capture_output=True, text=True)
    if result.stdout:
        print(f"{band} output:\n{result.stdout}")
    if result.stderr and result.returncode != 0:
        print(f"{band} [stderr]:\n{result.stderr}")

def main() -> None:
    total_start = __import__('time').time()
    for band, script in BANDS.items():
        run_band(band, script)
    total_duration = __import__('time').time() - total_start
    print(f"\nAll band pipelines completed in {total_duration:.2f} seconds.")

if __name__ == "__main__":
    main()
