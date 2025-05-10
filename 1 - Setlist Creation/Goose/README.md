# Goose Setlist Creation Pipeline

This directory contains the code and data pipeline for scraping, processing, and storing Goose setlist, song, show, and venue data from ElGoose.net and related sources.

## Directory Structure

- **Goose/**: Main Python package for scraping and data management.
- **Data Output**: All processed data is saved to `../../3 - Data/Goose/ElGoose/`.

## Modules Overview

### 1. `main.py`
- **Purpose**: Orchestrates the entire Goose data pipeline.
- **Workflow**:
  1. Loads song catalog (`loaders.py`)
  2. Loads show, venue, and tour data (`loaders.py`)
  3. Loads setlist and transition data (`loaders.py`)
  4. Saves all outputs to disk (`save_data.py`)
- **Logging**: Provides detailed logs for each step.

### 2. `call_api.py`
- **Functions**: `make_api_request`
- **Purpose**: Makes HTTP requests to the ElGoose.net API (v1/v2) and returns JSON data.

### 3. `loaders.py`
- **Functions**: `load_song_data`, `load_show_data`, `load_setlist_data`
- **Purpose**: Loads and processes data from the ElGoose.net API and website.
  - `load_song_data`: Merges API song data with scraped song metadata.
  - `load_show_data`: Loads show, venue, and tour data, handles past/future shows.
  - `load_setlist_data`: Loads setlist and transition data, processes columns.

### 4. `save_data.py`
- **Functions**: `save_goose_data`, `save_query_data`
- **Purpose**: Saves the processed DataFrames to CSV files and JSON files in the data directory.
  - `save_goose_data`: Handles saving all main data outputs and next show info.
  - `save_query_data`: Writes the last updated timestamp.

### 5. `utils.py`
- **Functions**: `get_data_dir`, `get_date_and_time`
- **Purpose**: Utility functions for managing data paths and timestamps.

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
