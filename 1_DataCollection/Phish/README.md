# Phish Data Collection Pipeline

## Overview

This pipeline collects and processes show, song, and setlist data for Phish. It primarily uses the Phish.net API and also scrapes additional metadata from the Phish.net website. An API key (`PHISH_API_KEY`) is required and should be configured in a `.env` file in the project root.

## Data Sources

- Phish.net API (v5)
- Phish.net website (for supplementary song metadata)

## Core Scripts

- `run_pipeline.py`: Orchestrates the entire data collection, processing, and saving workflow.
- `config.py`: Manages all Phish-specific configurations, including API endpoints, file paths, filenames, and logging settings.
- `call_api.py`: Handles authenticated requests to the Phish.net API.
- `loaders.py`: Fetches raw data from the API and website, performs initial processing and merging (e.g., song data, show data, setlist data).
- `export_data.py`: Saves the processed DataFrames to CSV files and relevant metadata (like last update timestamp and next show) to JSON files.
- `utils.py`: Contains utility functions specific to the Phish pipeline, if any, beyond common utilities.

## Data Output

All processed data is saved to `../../3_DataStorage/Phish/Collected/`.

Key files include:

- `songdata.csv`: Catalog of songs with details like original artist and debut date.
- `showdata.csv`: Information about each show, including date, venue, and tour.
- `venuedata.csv`: Details about venues where Phish has performed.
- `setlistdata.csv`: Setlist information for each show, including song order and transitions.
- `transitiondata.csv`: Information about song transitions.
- `last_updated.json`: Timestamp of the last successful pipeline run.
- `next_show.json`: Information about the next upcoming Phish show, if available.

## Configuration

- All pipeline settings are managed in `Phish/config.py`.
- Many settings can be overridden by environment variables (e.g., `PHISH_API_KEY`, `PHISH_DATA_DIR`).
- The `PHISH_API_KEY` must be set in a `.env` file in the project root directory (`/Users/connorkitchings/Desktop/Repositories/Concerts/.env`).

## Logging

- Logs are written to `../../logs/Phish/phish_pipeline.log`.
- Log rotation, level, and formatting are configured via `Phish/config.py` and the shared `logger.py` utility.

## How to Run

1. Ensure your `.env` file in the project root (`/Users/connorkitchings/Desktop/Repositories/Concerts/.env`) contains your `PHISH_API_KEY`.
2. Navigate to the Phish pipeline directory:

   ```bash
   cd /Users/connorkitchings/Desktop/Repositories/Concerts/1_DataCollection/Phish/
   ```

3. Execute the pipeline:

   ```bash
   python run_pipeline.py
   ```

## Dependencies

All dependencies are managed in the main `requirements.txt` file in the project root.
