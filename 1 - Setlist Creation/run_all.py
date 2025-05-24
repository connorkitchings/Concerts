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
from logging.handlers import RotatingFileHandler

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
    import time
    import threading
    script_full_path = os.path.join(BASE_DIR, script_path)
    print(f"\n===== Running {band} pipeline =====")
    logger: logging.Logger = logging.getLogger("band_pipeline")
    process = subprocess.Popen([
        sys.executable, script_full_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    def stream_output(stream) -> None:
        """Stream the output from the subprocess to both the terminal and the unified log file."""
        for line in iter(stream.readline, ''):
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
    Main entrypoint for running all band pipelines. Sets up unified file logging and runs each band pipeline in sequence.
    """
    # Set up unified file logging for the entire orchestration
    # Use an absolute path for the log file
    log_file: str = os.path.abspath(os.path.join(BASE_DIR, "../logs/data_pipeline.log"))
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger: logging.Logger = logging.getLogger("band_pipeline")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    total_start = __import__('time').time()
    for band, script in BANDS.items():
        logger.info(f"Starting {band} pipeline...")
        run_band(band, script)
        logger.info(f"Finished {band} pipeline.")
        for handler in logger.handlers:
            handler.flush()
    total_duration = __import__('time').time() - total_start
    logger.info(f"All band pipelines completed in {total_duration:.2f} seconds.")
    print(f"\nAll band pipelines completed in {total_duration:.2f} seconds.")

if __name__ == "__main__":
    main()
