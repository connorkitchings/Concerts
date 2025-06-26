"""
Module to run all four band prediction pipelines:
- Phish
- Goose
- UM
- WSP

Usage:
    python run_all.py
"""

import os
import subprocess
import sys
import time

# If you encounter 'Unable to import logger',
# run this script from the CK+ directory or ensure sys.path includes this directory.
from logger import get_logger

logger = get_logger(__name__)

BANDS = {
    "Phish": {
        "predict": "Phish/predict_today.py",
        "historical": "Phish/historical_testing.py",
    },
    "Goose": {
        "predict": "Goose/predict_today.py",
        "historical": "Goose/historical_testing.py",
    },
    "UM": {"predict": "UM/predict_today.py", "historical": "UM/historical_testing.py"},
    "WSP": {
        "predict": "WSP/predict_today.py",
        "historical": "WSP/historical_testing.py",
    },
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_band(band: str, scripts: dict) -> int:
    """
    Runs both predict_today.py and historical_testing.py for a band.
    """
    predict_path = os.path.join(BASE_DIR, scripts["predict"])
    hist_path = os.path.join(BASE_DIR, scripts["historical"])
    logger.info("Running %s CK+ prediction pipeline...", band)
    if not os.path.exists(predict_path):
        logger.error("predict_today.py not found for %s! (%s)", band, predict_path)
        return 1
    result_pred = subprocess.run(
        [sys.executable, predict_path], capture_output=True, text=True, check=False
    )
    if result_pred.stdout:
        logger.info("%s predict_today.py output:\n%s", band, result_pred.stdout)
    if result_pred.stderr and result_pred.returncode != 0:
        logger.error("%s predict_today.py [stderr]:\n%s", band, result_pred.stderr)
    if result_pred.returncode == 0:
        logger.info("Predictions for %s completed successfully.", band)
    else:
        logger.error(
            "Predictions for %s failed with exit code %s.", band, result_pred.returncode
        )
    # Now run historical_testing.py
    logger.info("Running %s CK+ accuracy update pipeline...", band)
    if not os.path.exists(hist_path):
        logger.error("historical_testing.py not found for %s! (%s)", band, hist_path)
        return 1
    result_hist = subprocess.run(
        [sys.executable, hist_path], capture_output=True, text=True, check=False
    )
    if result_hist.stdout:
        logger.info("%s historical_testing.py output:\n%s", band, result_hist.stdout)
    if result_hist.stderr and result_hist.returncode != 0:
        logger.error("%s historical_testing.py [stderr]:\n%s", band, result_hist.stderr)
    if result_hist.returncode == 0:
        logger.info("Accuracy update for %s completed successfully.", band)
    else:
        logger.error(
            "Accuracy update for %s failed with exit code %s.", band, result_hist.returncode
        )
    return result_pred.returncode or result_hist.returncode


def main() -> None:
    """
    Runs predict_today.py and historical_testing.py for all supported bands.
    """
    total_start = time.time()
    for band, scripts in BANDS.items():
        run_band(band, scripts)
    total_duration = time.time() - total_start
    logger.info(
        "All band prediction and accuracy pipelines completed in %.2f seconds.", total_duration
    )


if __name__ == "__main__":
    main()
