import subprocess
import os
from typing import List
from logger import get_logger

logger = get_logger(__name__)

BANDS = ["WSP", "Phish", "Goose", "UM"]


def run_predict_today(band: str) -> int:
    """
    Runs the predict_today.py script for a given band.

    Args:
        band (str): The band subdirectory (e.g., 'WSP', 'Phish', 'Goose', 'UM')

    Returns:
        int: The exit code from the subprocess call.
    """
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), band)
    script_path = os.path.join(script_dir, "predict_today.py")
    if not os.path.isfile(script_path):
        logger.error(f"predict_today.py not found for {band} at {script_path}")
        return 1
    logger.info(f"Running predictions for {band}...")
    result = subprocess.run(["python3", script_path], cwd=script_dir)
    if result.returncode == 0:
        logger.info(f"Predictions for {band} completed successfully.")
    else:
        logger.error(f"Predictions for {band} failed with exit code {result.returncode}.")
    return result.returncode


def main() -> None:
    """
    Runs predict_today.py for all supported bands.
    """
    failures: List[str] = []
    for band in BANDS:
        code = run_predict_today(band)
        if code != 0:
            failures.append(band)
    if failures:
        logger.error(f"Predictions failed for: {', '.join(failures)}")
    else:
        logger.info("All band predictions completed successfully.")


if __name__ == "__main__":
    main()
