# UM Setlist Creation Pipeline

This directory contains the code and data pipeline for scraping, processing, and storing Umphrey’s McGee (UM) setlist, song, and venue data from allthings.umphreys.com.

## Directory Structure

- **UM/**: Main Python package for scraping and data management.
- **Data Output**: All processed data is saved to `../../3 - Data/UM/AllThingsUM/`.

## Modules Overview

### 1. `main.py`
- **Purpose**: Orchestrates the entire UM data pipeline.
- **Workflow**:
  1. Scrapes the full UM song catalog (`scrape_songs.py`).
  2. Scrapes the full UM venue catalog (`scrape_shows.py`).
  3. Updates setlist data using the incremental update method (`incremental_um_setlist_update`), which fetches setlists for the last year and current year only, appends new data, and removes duplicates. (Switch to `full_um_setlist_update` in code for a full historical refresh.)
  4. Sorts setlist data by most recent date and set order before saving.
  5. Saves all outputs to disk (`save_data.py`).
  6. Updates `last_updated.json` and `next_show.json` after a successful run.
- **Logging**: Provides detailed logs for each step.
- **Note**: The pipeline is designed for efficient incremental updates but supports full refresh if needed by modifying the update method in `main.py`.

### 2. `scrape_songs.py`
- **Function**: `scrape_um_songs`
- **Purpose**: Scrapes the UM song catalog from allthings.umphreys.com.
- **Outputs**: DataFrame with song metadata.
- **Key Columns**: `Song Name`, `Original Artist`, `Debut Date`, `Last Played`, `Times Played Live`, `Avg Show Gap`.

### 3. `scrape_shows.py`
- **Function**: `scrape_um_shows`
- **Purpose**: Scrapes the UM venue catalog from allthings.umphreys.com.
- **Outputs**: DataFrame with venue metadata.
- **Key Columns**: `Venue Name`, `City`, `State`, `Country`, `Times Played`, `Last Played`.

### 4. `scrape_setlists.py`
- **Functions**: `full_um_setlist_update`, `incremental_um_setlist_update`, `_sort_setlist_df`, `save_um_setlist_data`, `load_existing_data`, `get_last_update_time`
- **Purpose**:
  - `full_um_setlist_update`: Fetches and builds a complete setlist dataset for all years (1998–present) from the UM website.
  - `incremental_um_setlist_update`: Efficiently fetches setlists for just the last and current year, appends to existing data, and removes duplicates.
  - `_sort_setlist_df`: Sorts setlist data by most recent date and set order (using custom set label logic).
  - `save_um_setlist_data`: Sorts and saves setlist data to disk.
  - `load_existing_data`: Loads existing song, venue, and setlist data from disk.
  - `get_last_update_time`: Reads the last update timestamp from `last_updated.json`.
- **Outputs**: DataFrame with detailed setlist information for each show, always sorted by most recent date and set order.

### 5. `save_data.py`
- **Functions**: `save_um_data`, `save_query_data`
- **Purpose**: Saves the processed DataFrames to CSV files in the data directory. Writes:
  - `last_updated.json`: Timestamp of last data update.
  - `next_show.json`: Metadata for the next upcoming show.
- **Files Created**: `songdata.csv`, `venuedata.csv`, `setlistdata.csv`, `last_updated.json`, `next_show.json`.

### 6. `utils.py`
- **Functions**: 
  - `get_data_dir`: Returns the path to the data directory.
  - `get_date_and_time`: Returns the current date and time as a string.

---

## Data Outputs

All data is stored in `3 - Data/UM/AllThingsUM/`:

| File                | Description                                                               |
|---------------------|---------------------------------------------------------------------------|
| `songdata.csv`      | Song catalog: song name, original artist, debut/last played, play counts, avg gap. |
| `venuedata.csv`     | Venue metadata: venue name, city, state, country, play counts, last played.|
| `setlistdata.csv`   | Song-by-song setlist data for each show (very large file).                |
| `last_updated.json` | Timestamp of the most recent pipeline run.                                |
| `next_show.json`    | Metadata for the next scheduled UM show.                                  |

### Example: `songdata.csv` Columns

- `Song Name`: Name of the song
- `Original Artist`: Artist if cover
- `Debut Date`: Date first played
- `Last Played`: Date last played
- `Times Played Live`: Number of times played
- `Avg Show Gap`: Average number of shows between plays

### Example: `venuedata.csv` Columns

- `Venue Name`: Name of the venue
- `City`, `State`, `Country`
- `Times Played`: Number of shows at the venue
- `Last Played`: Date of last show at the venue

### Example: `setlistdata.csv` Columns

- Columns may include: `Date Played`, `Song Name`, `Show Date`, `Footnote`, etc.
- Each row represents a song played at a specific show.

---

## Pipeline Context

- The pipeline is designed for reproducibility and automated updates.
- Data is scraped directly from allthings.umphreys.com, ensuring up-to-date information.
- All modules are highly modular, allowing for extension or adaptation.

---

## Running the Pipeline

Run `main.py` to execute the full scraping and data-saving process. All required dependencies are standard (requests, pandas, BeautifulSoup, etc.).

- By default, the pipeline performs an **incremental setlist update** (last year and current year only, fast).
- To perform a **full setlist update** (all years, slow), edit the update method in `main.py` to use `full_um_setlist_update` instead of `incremental_um_setlist_update`.

No command-line flags are required; behavior is controlled in code for reliability and reproducibility.
