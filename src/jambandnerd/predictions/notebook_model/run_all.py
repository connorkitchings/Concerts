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

from logger import get_logger

logger = get_logger(__name__)

BANDS = {
    "Phish": {
        "predict": "Phish/predict_today.py",
        "accuracy": "Phish/historical_testing.py",
    },
    "Goose": {
        "predict": "Goose/predict_today.py",
        "accuracy": "Goose/historical_testing.py",
    },
    "UM": {"predict": "UM/predict_today.py", "accuracy": "UM/historical_testing.py"},
    "WSP": {"predict": "WSP/predict_today.py"},
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_band(band: str, script_paths: dict) -> int:
    """
    Runs the prediction pipeline for a given band.
    Args:
        band: Name of the band.
        script_paths: Dict with 'predict' script relative path.
    Returns:
        Exit code for the prediction script (0 if succeeds).
    """
    predict_path = os.path.join(BASE_DIR, script_paths["predict"])
    code_sum = 0
    # Run prediction pipeline
    logger.info(f"Running {band} prediction pipeline...")
    if not os.path.exists(predict_path):
        logger.error(f"predict_today.py not found for {band}! ({predict_path})")
        code_sum += 1
    else:
        result = subprocess.run(
            [sys.executable, predict_path], capture_output=True, text=True
        )
        if result.stdout:
            logger.info(f"{band} predict_today.py output:\n{result.stdout}")
        if result.stderr and result.returncode != 0:
            logger.error(f"{band} predict_today.py [stderr]:\n{result.stderr}")
        if result.returncode == 0:
            logger.info(f"Predictions for {band} completed successfully.")
        else:
            logger.error(
                f"Predictions for {band} failed with exit code {result.returncode}."
            )
        code_sum += result.returncode
    return code_sum


def main() -> None:
    """
    Runs predict_today.py for all supported bands.
    """
    total_start = time.time()
    for band, scripts in BANDS.items():
        run_band(band, scripts)
    total_duration = time.time() - total_start
    logger.info(
        f"All band prediction pipelines completed in {total_duration:.2f} seconds."
    )


if __name__ == "__main__":
    main()
