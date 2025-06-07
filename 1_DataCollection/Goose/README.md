# Goose Setlist Creation Pipeline

This directory contains the code and data pipeline for scraping, processing, and storing Goose setlist, song, show, and venue data from ElGoose.net and related sources.

## Directory Structure

- **Goose/**: Main Python package for scraping and data management.
- **Data Output**: All processed data is saved to `../../3 - Data/Goose/ElGoose/`.

## Modules Overview

### 1. `run_pipeline.py`
- **Purpose**: Orchestrates the entire Goose data pipeline.
- **Workflow**:
  1. Loads song catalog (`loaders.py`)
  2. Loads show, venue, and tour data (`loaders.py`)
  3. Loads setlist and transition data (`loaders.py`)
  4. Saves all outputs to disk (`export_data.py`)
- **Modular Logging**: Goose uses its own `logger.py`, wrapping a shared general logger utility. Logs are always written to the correct, config-driven location for Goose, as set in `config.py`. This prevents cross-band log contamination and makes the logging system robust and easy to maintain.

### 2. `config.py`
- **Purpose**: Centralized configuration for all paths, filenames, logging, and environment variable overrides.
- **How to use**: Adjust settings via environment variables or edit `config.py` directly. See below for available variables.

### Logging System

Goose has its own `logger.py` that wraps a shared general logger utility. The logger is always configured using Goose's `config.py` settings (`LOG_FILE`, `LOG_LEVEL`, etc.), ensuring that logs are written to the correct location and never overlap with other bands. To change log location or settings, update the environment variables or `Goose/config.py`.

### 3. `call_api.py`
- **Functions**: `make_api_request`
- **Purpose**: Makes HTTP requests to the ElGoose.net API (v1/v2) and returns JSON data.

### 4. `loaders.py`
- **Functions**: `load_song_data`, `load_show_data`, `load_setlist_data`
- **Purpose**: Loads and processes data from the ElGoose.net API and website.
  - `load_song_data`: Merges API song data with scraped song metadata.
  - `load_show_data`: Loads show, venue, and tour data, handles past/future shows.
  - `load_setlist_data`: Loads setlist and transition data, processes columns.

### 5. `export_data.py`
- **Functions**: `save_goose_data`, `save_query_data`
- **Purpose**: Saves the processed DataFrames to CSV files and JSON files in the data directory.
  - `save_goose_data`: Handles saving all main data outputs and next show info.
  - `save_query_data`: Writes the last updated timestamp.

### 6. `utils.py`
- **Functions**: `print_relative_path`, `get_date_and_time`
- **Purpose**: Utility functions for managing data paths and timestamps. All functions include type hints and Google-style docstrings.

---

## Configuration & Environment Variables

All pipeline settings are managed via `config.py` and can be overridden with environment variables. Key variables include:

- `GOOSE_DATA_DIR`: Path to the data directory.
- `GOOSE_LOG_DIR`: Path to the log directory.
- `GOOSE_BAND_NAME`: Band name (default: 'Goose').
- `GOOSE_SONG_DATA_FILENAME`, `GOOSE_SHOW_DATA_FILENAME`, etc.: Output file names.
- `GOOSE_LOG_LEVEL`, `GOOSE_LOG_MAX_BYTES`, `GOOSE_LOG_BACKUP_COUNT`: Logging settings.

Update your environment or `.env` file to customize the pipeline without changing code.

## Logging

- Logs are written to the directory specified by `GOOSE_LOG_DIR` (default: `../../logs/Setlist_Creation/Goose/`).
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

All outputs are saved in `../../3 - Data/Goose/ElGoose/`:

### 1. `songdata.csv`
- **Description**: Catalog of Goose songs with metadata.
- **Columns**: `song_id`, `song`, `is_original`, `original_artist`, `debut_date`, `last_played`, `times_played`, `avg_show_gap`

### 2. `showdata.csv`
- **Description**: Metadata for each Goose show.
- **Columns**: `show_number`, `show_id`, `show_date`, `venue_id`, `tour_id`, `show_order`

### 3. `venuedata.csv`
- **Description**: Venue information for all Goose shows.
- **Columns**: `venue_id`, `venuename`, `city`, `state`, `country`, `location`

### 4. `setlistdata.csv`
- **Description**: Detailed setlist information for each show.
- **Columns**: `uniqueid`, `show_id`, `song_id`, `setnumber`, `position`, `tracktime`, `transition_id`, `isreprise`, `isjam`, `footnote`, `isjamchart`, `jamchart_notes`, `soundcheck`, `isverified`, `isrecommended`

### 5. `transitiondata.csv`
- **Description**: Information on song transitions (e.g., segues, teases).
- **Columns**: `transition_id`, `transition`

### 6. `last_updated.json`
- **Description**: Timestamp of the last update to the data pipeline.
- **Format**: `{ "last_updated": "MM/DD/YYYY HH:MM" }`

### 7. `next_show.json`
- **Description**: Metadata for the next scheduled Goose show.
- **Format**: `{ "next_show": { "show_number": int, "show_id": int, "show_date": str, "venue_id": int, "tour_id": str, "show_order": int } }`

---

## How to Run

1. Install dependencies (see requirements.txt if present).
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
