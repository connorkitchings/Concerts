"""
Module to run all four band prediction pipelines:
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
import time

try:
    from logger import get_logger
except ImportError:
    def get_logger(name):
        class DummyLogger:
            def info(self, msg): print(msg)
            def error(self, msg): print(msg)
        return DummyLogger()

BANDS = {
    "Phish": "Phish/predict_today.py",
    "Goose": "Goose/predict_today.py",
    "UM": "UM/predict_today.py",
    "WSP": "WSP/predict_today.py",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_band(band, script_path, logger):
    script_full_path = os.path.join(BASE_DIR, script_path)
    logger.info(f"Running {band} prediction pipeline...")
    if not os.path.exists(script_full_path):
        logger.error(f"predict_today.py not found for {band}! ({script_full_path})")
        return
    result = subprocess.run([sys.executable, script_full_path], capture_output=True, text=True)
    if result.stdout:
        logger.info(f"{band} output:\n{result.stdout}")
    if result.stderr and result.returncode != 0:
        logger.error(f"{band} [stderr]:\n{result.stderr}")

def main():
    logger = get_logger(__name__)
    total_start = time.time()
    for band, script in BANDS.items():
        run_band(band, script, logger)
    total_duration = time.time() - total_start
    logger.info(f"All band prediction pipelines completed in {total_duration:.2f} seconds.")

if __name__ == "__main__":
    main()
