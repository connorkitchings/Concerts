# Phish Setlist Creation Pipeline

This directory contains the code and data pipeline for scraping, processing, and storing Phish setlist, song, show, and venue data from Phish.net and related sources.

## Directory Structure

- **Phish/**: Main Python package for scraping and data management.
- **Data Output**: All processed data is saved to `../../3 - Data/Phish/PhishNet/`.

## Modules Overview

### 1. `run_pipeline.py`
- **Purpose**: Orchestrates the entire Phish data pipeline.
- **Workflow**:
  1. Loads API credentials (from env or credentials file)
  2. Loads song catalog (`loaders.py`)
  3. Loads show and venue data (`loaders.py`)
  4. Loads setlist and transition data (`loaders.py`)
  5. Saves all outputs to disk (`export_data.py`)
- **Modular Logging**: Phish uses its own `logger.py`, wrapping a shared general logger utility. Logs are always written to the correct, config-driven location for Phish, as set in `config.py`. This prevents cross-band log contamination and makes the logging system robust and easy to maintain.

### 2. `config.py`
- **Purpose**: Centralized configuration for all paths, filenames, logging, and environment variable overrides.
- **How to use**: Adjust settings via environment variables or edit `config.py` directly. See below for available variables.

### Logging System

Phish has its own `logger.py` that wraps a shared general logger utility. The logger is always configured using Phish's `config.py` settings (`LOG_FILE`, `LOG_LEVEL`, etc.), ensuring that logs are written to the correct location and never overlap with other bands. To change log location or settings, update the environment variables or `Phish/config.py`.

### 3. `call_api.py`
- **Functions**: `access_credentials`, `make_api_request`
- **Purpose**: Handles API key retrieval and makes authenticated requests to the Phish.net API.

### 4. `loaders.py`
- **Functions**: `load_song_data`, `load_show_data`, `load_setlist_data`
- **Purpose**: Loads and processes data from the Phish.net API and phish.net website.
  - `load_song_data`: Merges API song data with scraped song metadata.
  - `load_show_data`: Loads show and venue data, handles past/future shows.
  - `load_setlist_data`: Loads setlist and transition data, processes columns.

### 5. `export_data.py`
- **Functions**: `save_phish_data`, `save_query_data`
- **Purpose**: Saves the processed DataFrames to CSV files and JSON files in the data directory.
  - `save_phish_data`: Writes all major data files, including next show info.
  - `save_query_data`: Writes the last update timestamp.
- **Files Created**: `songdata.csv`, `showdata.csv`, `venuedata.csv`, `setlistdata.csv`, `transitiondata.csv`, `last_updated.json`, `next_show.json`.

### 6. `utils.py`
- **Functions**: `print_relative_path`, `get_date_and_time`
- **Purpose**: Utility functions for path management and timestamps. All functions include type hints and Google-style docstrings.

---

## Configuration & Environment Variables

All pipeline settings are managed via `config.py` and can be overridden with environment variables. Key variables include:

- `PHISH_DATA_DIR`: Path to the data directory.
- `PHISH_LOG_DIR`: Path to the log directory.
- `PHISH_BAND_NAME`: Band name (default: 'Phish').
- `PHISH_SONG_DATA_FILENAME`, `PHISH_SHOW_DATA_FILENAME`, etc.: Output file names.
- `PHISH_LOG_LEVEL`, `PHISH_LOG_MAX_BYTES`, `PHISH_LOG_BACKUP_COUNT`: Logging settings.
- `PHISH_API_KEY`: API key for Phish.net.

Update your environment or `.env` file to customize the pipeline without changing code.

## Logging

- Logs are written to the directory specified by `PHISH_LOG_DIR` (default: `../../logs/Setlist_Creation/Phish/`).
- Log rotation and level are controlled via environment variables or `config.py`.
- All major steps and errors are logged for traceability.

## Type Hints & Docstrings

- All Python code uses type hints for function signatures and variables.
- All functions and classes include Google-style docstrings for clarity and maintainability.

## Usage

1. Set up your environment variables as needed (see above).
2. Run the pipeline:
   ```bash
   python run_pipeline.py
   ```
3. Outputs will be saved to the data directory and logs to the log directory.

---

---

## Data Outputs

All data is stored in `3 - Data/Phish/PhishNet/`:

| File                | Description                                                               |
|---------------------|---------------------------------------------------------------------------|
| `songdata.csv`      | Song catalog: song_id, song name, original artist, debut date.             |
| `showdata.csv`      | Show metadata: show number, id, date, venue, tour, notes, stats.           |
| `venuedata.csv`     | Venue metadata: venue id, name, city, state, country.                      |
| `setlistdata.csv`   | Song-by-song setlist data for each show (very large file).                 |
| `transitiondata.csv`| Setlist transition types and symbols.                                      |
| `last_updated.json` | Timestamp of the most recent pipeline run.                                 |
| `next_show.json`    | Metadata for the next scheduled Phish show.                                |

### Example: `songdata.csv` Columns
- `song_id`: Unique ID for the song
- `song`: Name of the song
- `original_artist`: Artist if cover
- `debut_date`: Date first played

### Example: `showdata.csv` Columns
- `show_number`: Sequential show number
- `showid`: Unique show ID
- `showdate`: Date of the show
- `venueid`: Venue ID
- `tourid`: Tour ID
- `exclude_from_stats`: Exclusion flag
- `setlist_notes`: Notes for the show

### Example: `venuedata.csv` Columns
- `venueid`: Unique venue ID
- `venue`: Name of the venue
- `city`, `state`, `country`

### Example: `setlistdata.csv` Columns
- Columns may include: `showid`, `uniqueid`, `songid`, `set`, `position`, `transition`, `isreprise`, `isjam`, `isjamchart`, `jamchart_description`, `tracktime`, `gap`, `is_original`, `soundcheck`, `footnote`, `exclude`
- Each row represents a song played at a specific show.

### Example: `transitiondata.csv` Columns
- `transition`: Symbol or type (e.g., ",", ">", "->", etc.)
- `trans_mark`: Transition mark or description

---

## Pipeline Context
- The pipeline is designed for reproducibility and automated updates.
- Data is scraped directly from Phish.net and related sources, ensuring up-to-date information.
- All modules are highly modular, allowing for extension or adaptation.

---

## Running the Pipeline

Run `main.py` to execute the full scraping and data-saving process. All required dependencies are standard (requests, pandas, BeautifulSoup, etc.). API key for Phish.net is required (see `call_api.py`).
