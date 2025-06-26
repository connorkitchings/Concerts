"""
Module to run all four setlist creation pipelines:
- Phish
- Goose
- UM
- WSP

Usage:
    python run_all.py

This script runs each band's pipeline via its dedicated run_pipeline.py entrypoint.
Logging for this orchestration script is handled by the centralized logger.py,
using configurations from common_config.py.
"""

import logging
import os
import subprocess
import sys
import threading
import time
from logging.handlers import RotatingFileHandler

# Set up logging with mm-dd-yyyy hh:mm:ss format
LOG_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "logs", "run_all_pipelines.log"
)
LOG_FILE_PATH = os.path.abspath(LOG_FILE_PATH)
LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%m-%d-%Y %H:%M:%S"
if not os.path.exists(os.path.dirname(LOG_FILE_PATH)):
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        RotatingFileHandler(LOG_FILE_PATH, maxBytes=5 * 1024 * 1024, backupCount=3),
        logging.StreamHandler(sys.stdout),
    ],
)

# Define the main scripts for each band (use run_pipeline.py for consistency)
BANDS = {
    "Goose": "run_goose_pipeline.py",
    "Phish": "run_phish_pipeline.py",
    "UM": "run_um_pipeline.py",
    "WSP": "run_wsp_pipeline.py",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_band(band: str, script_path: str) -> None:
    """
    Run the pipeline for a single band and stream output to both terminal and unified log file.

    Args:
        band (str): Name of the band.
        script_path (str): Relative path to the band's run_pipeline.py.
    """
    script_full_path = os.path.join(BASE_DIR, script_path)
    logger = logging.getLogger("run_all_pipeline")
    process = subprocess.Popen(
        [sys.executable, script_full_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    def stream_output(stream) -> None:
        """Stream the output from the subprocess to both the terminal and the unified log file."""
        for line in iter(stream.readline, ""):
            line = line.rstrip()
            if line:
                msg = f"[{band}] {line}"
                print(msg)
                logger.info(msg)
        stream.close()

    threads = [
        threading.Thread(target=stream_output, args=(process.stdout,)),
        threading.Thread(target=stream_output, args=(process.stderr,)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    process.wait()
    if process.returncode != 0:
        msg = f"{band} pipeline exited with code {process.returncode}"
        print(msg)
        logger.error(msg)
    else:
        msg = f"{band} pipeline completed successfully."
        logger.info(msg)


def main() -> None:
    """
    Main entrypoint for running all band pipelines.
    Sets up unified file logging and runs each band pipeline in parallel.
    """
    logger = logging.getLogger("run_all_pipeline")
    logger.info("Running all band pipelines in parallel...")
    # Ensure all log directories exist
    log_dirs = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "Phish"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "Goose"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "UM"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "WSP"),
    ]
    for d in log_dirs:
        os.makedirs(d, exist_ok=True)
    total_start = time.time()
    threads = []
    for band, script in BANDS.items():
        t = threading.Thread(
            target=run_band, args=(band, script), name=f"{band}_thread"
        )
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    total_duration = time.time() - total_start
    logger.info("All band pipelines completed in %.2f seconds.", total_duration)
    print(f"All band pipelines completed in {total_duration:.2f} seconds.")
    logging.shutdown()  # Ensure all logs are flushed


if __name__ == "__main__":
    main()
