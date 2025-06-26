# Widespread Panic (WSP) Data Collection Pipeline

## Overview

This pipeline collects and processes show, song, and setlist data for Widespread Panic (WSP). It scrapes data directly from everydaycompanion.com. This pipeline does not require an API key.

## Data Sources

- everydaycompanion.com (website scraping)

## Core Scripts

- `run_pipeline.py`: Orchestrates the entire data collection, processing, and saving workflow.
- `config.py`: Manages all WSP-specific configurations, including URLs, file paths, filenames, and logging settings.
- `scrape_shows.py`: Scrapes show metadata.
- `scrape_songs.py`: Scrapes the song catalog.
- `scrape_setlists.py`: Scrapes setlist data for shows.
- `export_data.py`: Saves the processed DataFrames to CSV files and relevant metadata (like last update timestamp and next show) to JSON files.
- `utils.py`: Contains utility functions specific to the WSP pipeline.

## Data Output

All processed data is saved to `data/wsp/collected/` (relative to project root).

Key files include:

- `songdata.csv`: Catalog of songs with details.
- `showdata.csv`: Information about each show.
- `setlistdata.csv`: Setlist information for each show.
- `last_updated.json`: Timestamp of the last successful pipeline run.
- `next_show.json`: Information about the next upcoming WSP show, if available.

### Example: `songdata.csv` Columns

- `ftp`: First time played (date)
- `ltp`: Last time played (date)
- `times_played`: Number of times played
- `aka`: Also known as (alternate titles)

### Example: `showdata.csv` Columns

- `date`, `year`, `month`, `day`, `weekday`, `venue`, `city`, `state`
- `show_index_overall`, `show_index_withinyear`, `run_index`
- `venue_full`: Full venue description
- `link`: URL to setlist

### Example: `setlistdata.csv` Columns

- `song_name`: Name of the song played
- `set`: Set number or encore
- `song_index_set`: Song's position within the set
- `song_index_show`: Song's position within the show
- `into`: Indicates segue/transition (1/0)
- `song_note_detail`: Notes about the song (e.g., guests, teases)
- `link`: Show link

## Configuration

- All configuration is now managed directly within each script. There is no config.py or shared utilities. All constants (paths, URLs, filenames) are defined at the top of each script, and logging uses the shared jambandnerd.log package for consistency with the Phish, Goose, and UM modules.
- No API key is required for this pipeline.

## Logging

- Logs are written to `../../logs/jambandnerd.log`.

## How to Run

1. Navigate to the WSP pipeline directory:

   ```bash
   cd /Users/connorkitchings/Desktop/Repositories/Concerts/1_DataCollection/WSP/
   ```

2. Execute the pipeline:

   ```bash
   python run_pipeline.py
   ```

## Dependencies

All dependencies are managed in the main `requirements.txt` file in the project root.
