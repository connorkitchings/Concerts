# Phish Setlist Creation Pipeline

This directory contains the code and data pipeline for scraping, processing, and storing Phish setlist, song, show, and venue data from Phish.net and related sources.

## Directory Structure

- **Phish/**: Main Python package for scraping and data management.
- **Data Output**: All processed data is saved to `../../3 - Data/Phish/PhishNet/`.

## Modules Overview

### 1. `main.py`
- **Purpose**: Orchestrates the entire Phish data pipeline.
- **Workflow**:
  1. Loads API credentials (from env or credentials file)
  2. Loads song catalog (`loaders.py`)
  3. Loads show and venue data (`loaders.py`)
  4. Loads setlist and transition data (`loaders.py`)
  5. Saves all outputs to disk (`save_data.py`)
- **Logging**: Provides detailed logs for each step.

### 2. `call_api.py`
- **Functions**: `access_credentials`, `make_api_request`
- **Purpose**: Handles API key retrieval and makes authenticated requests to the Phish.net API.

### 3. `loaders.py`
- **Functions**: `load_song_data`, `load_show_data`, `load_setlist_data`
- **Purpose**: Loads and processes data from the Phish.net API and phish.net website.
  - `load_song_data`: Merges API song data with scraped song metadata.
  - `load_show_data`: Loads show and venue data, handles past/future shows.
  - `load_setlist_data`: Loads setlist and transition data, processes columns.

### 4. `save_data.py`
- **Functions**: `save_phish_data`, `save_query_data`
- **Purpose**: Saves the processed DataFrames to CSV files and JSON files in the data directory.
  - `save_phish_data`: Writes all major data files, including next show info.
  - `save_query_data`: Writes the last update timestamp.
- **Files Created**: `songdata.csv`, `showdata.csv`, `venuedata.csv`, `setlistdata.csv`, `transitiondata.csv`, `last_updated.json`, `next_show.json`.

### 5. `utils.py`
- **Functions**: `get_data_dir`, `get_date_and_time`
- **Purpose**: Utility functions for path management and timestamps.

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
