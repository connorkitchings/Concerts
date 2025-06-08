# Goose Data Collection Pipeline

## Overview

This pipeline collects and processes show, song, setlist, and tour data for Goose. It primarily uses the elgoose.net API and also scrapes additional metadata from the elgoose.net website. This pipeline does not require an API key.

## Data Sources

- elgoose.net API (v1/v2)
- elgoose.net website (for supplementary song metadata)

## Core Scripts

- `run_pipeline.py`: Orchestrates the entire data collection, processing, and saving workflow.
- `config.py`: Manages all Goose-specific configurations, including API endpoints, file paths, filenames, and logging settings.
- `call_api.py`: Handles requests to the elgoose.net API.
- `loaders.py`: Fetches raw data from the API and website, performs initial processing and merging (e.g., song data, show data, venue data, tour data, setlist data).
- `export_data.py`: Saves the processed DataFrames to CSV files and relevant metadata (like last update timestamp and next show) to JSON files.
- `utils.py`: Contains utility functions specific to the Goose pipeline.

## Data Output

All processed data is saved to `../../3_DataStorage/Goose/Collected/`.

Key files include:

- `songdata.csv`: Catalog of songs with details like original artist and debut date.
- `showdata.csv`: Information about each show, including date, venue, and tour.
- `venuedata.csv`: Details about venues where Goose has performed.
- `tourdata.csv`: Information about Goose tours.
- `setlistdata.csv`: Setlist information for each show, including song order and transitions.
- `transitiondata.csv`: Information about song transitions.
- `last_updated.json`: Timestamp of the last successful pipeline run.
- `next_show.json`: Information about the next upcoming Goose show, if available.

## Configuration

- All pipeline settings are managed in `Goose/config.py`.
- Many settings can be overridden by environment variables.

## Logging

- Logs are written to `../../logs/Goose/goose_pipeline.log`.
- Log rotation, level, and formatting are configured via `Goose/config.py` and the shared `logger.py` utility.

## How to Run

1. Navigate to the Goose pipeline directory:
2. Run `main.py` to execute the full pipeline:

   ```bash
   python main.py
   ```

3. All outputs will be updated in the data directory.

---

## Notes

- The pipeline is modular and can be extended for additional data sources or analytics.
- Logging is provided for debugging and auditability.
- For questions or issues, please refer to the code comments or contact the maintainer.
