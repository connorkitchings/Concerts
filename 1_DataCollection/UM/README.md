# Umphrey's McGee (UM) Data Collection Pipeline

## Overview

This pipeline collects and processes show, song, venue, and setlist data for Umphrey's McGee (UM). It scrapes data directly from allthings.umphreys.com. This pipeline does not require an API key.

## Data Sources

- allthings.umphreys.com (website scraping)

## Core Scripts

- `main.py`: Orchestrates the entire data collection, processing, and saving workflow.
- `config.py`: Manages all UM-specific configurations, including URLs, file paths, filenames, and logging settings.
- `scrape_songs.py`: Scrapes song catalog information.
- `scrape_shows.py`: Scrapes venue information and processes show data.
- `scrape_setlists.py`: Scrapes detailed setlist information.
- `save_data.py`: Saves the processed DataFrames to CSV files and relevant metadata to JSON files.
- `utils.py`: Contains utility functions specific to the UM pipeline.

## Data Output

All processed data is saved to `../../3_DataStorage/UM/Collected/`.

Key files include:

- `songdata.csv`: Catalog of songs with details.
- `venuedata.csv`: Information about venues where UM has performed.
- `showdata.csv`: Information about each show, including date, venue, and other details.
- `setlistdata.csv`: Detailed setlist information for each show.
- `last_updated.json`: Timestamp of the last successful pipeline run.
- `next_show.json`: Information about the next upcoming UM show, if available.

## Configuration

- All pipeline settings are managed in `UM/config.py`.
- Many settings can be overridden by environment variables (e.g., `UM_DATA_DIR`, `UM_SCRAPE_YEARS`).
- No API key is required for this pipeline.

## Logging

- Logs are written to `../../logs/UM/um_pipeline.log`.
- Log rotation, level, and formatting are configured via `UM/config.py` and the shared `logger.py` utility.

## How to Run

1. Navigate to the UM pipeline directory:

   ```bash
   cd /Users/connorkitchings/Desktop/Repositories/Concerts/1_DataCollection/UM/
   ```

2. Execute the pipeline:

   ```bash
   python main.py
   ```

   *Note: By default, the pipeline performs an incremental setlist update. To perform a full historical update, you may need to modify the call within `main.py` (e.g., to use a function like `full_um_setlist_update` if available in `scrape_setlists.py`).*

## Dependencies

All dependencies are managed in the main `requirements.txt` file in the project root.
