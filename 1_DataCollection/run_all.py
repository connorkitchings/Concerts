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

import logging  # Added to resolve NameError
import os
import subprocess
import sys
import threading
import time  # Standardized import

import common_config  # Import common configuration for logging path
from logger import get_logger  # Use centralized logger

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
    Run the pipeline for a single band and stream output to both terminal and unified log file.

    Args:
        band (str): Name of the band.
        script_path (str): Relative path to the band's run_pipeline.py.
    """
    script_full_path = os.path.join(BASE_DIR, script_path)
    # Get the main logger instance, configured by main()
    main_logger = logging.getLogger("run_all_pipeline")  # Consistent logger name
    main_logger.info(f"===== Running {band} pipeline =====")
    print(f"\n===== Running {band} pipeline =====")
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
                main_logger.info(msg)  # Use the main_logger instance
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
        main_logger.error(msg)  # Use the main_logger instance
    else:
        msg = f"{band} pipeline completed successfully."
        main_logger.info(msg)  # Use the main_logger instance


def main() -> None:
    """
    Main entrypoint for running all band pipelines. Sets up unified file logging and runs each band pipeline in sequence.
    """
    # Initialize the main logger for the run_all.py script itself
    # It will use settings from common_config.py via get_logger
    # The log file path is common_config.LOG_FILE_PATH
    logger = get_logger(
        name="run_all_pipeline",  # Specific name for this orchestrator's logs
        log_file=common_config.LOG_FILE_PATH,
        # log_level, log_max_bytes, log_backup_count will use defaults from common_config
        add_console_handler=True,  # Keep console output for run_all.py itself
    )

    total_start = time.time()
    for band, script in BANDS.items():
        logger.info(f"Starting {band} pipeline...")
        run_band(
            band, script
        )  # run_band will use the 'logger' instance obtained via getLogger("run_all_pipeline")
        logger.info(f"Finished {band} pipeline.")
        # No need to manually flush, RotatingFileHandler handles it.
    total_duration = time.time() - total_start
    logger.info(f"All band pipelines completed in {total_duration:.2f} seconds.")
    print(f"\nAll band pipelines completed in {total_duration:.2f} seconds.")
    logging.shutdown()  # Ensure all logs are flushed


if __name__ == "__main__":
    main()
