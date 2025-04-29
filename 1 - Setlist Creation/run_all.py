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
from logger import get_logger
import logging

# Define the main scripts for each band
BANDS = {
    "Phish": "Phish/main.py",
    "Goose": "Goose/main.py",
    "UM": "UM/main.py",
    "WSP": "WSP/main.py",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_band(band, script_path, logger):
    import time
    script_full_path = os.path.join(BASE_DIR, script_path)
    logger.info(f"Running {band} pipeline")
    start_time = time.time()
    result = subprocess.run([sys.executable, script_full_path], capture_output=True, text=True)
    duration = time.time() - start_time
    if result.stdout:
        logger.info(f"{band} output:\n{result.stdout}")
    if result.stderr and result.returncode != 0:
        logger.error(f"{band} [stderr]:\n{result.stderr}")
    logger.info(f"Finished {band} pipeline in {duration:.2f} seconds.")

def main():
    # Add blank line to log file to separate runs
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'Setlist_Creation')
    log_file = os.path.join(log_dir, 'setlist_scraper.log')
    with open(log_file, 'a') as f:
        f.write('\n')
    logger = get_logger(__name__)
    total_start = __import__('time').time()
    for band, script in BANDS.items():
        run_band(band, script, logger)
    total_duration = __import__('time').time() - total_start
    logger.info(f"All band pipelines completed in {total_duration:.2f} seconds.")

if __name__ == "__main__":
    main()
