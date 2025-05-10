# UM Setlist Creation Pipeline

This directory contains the code and data pipeline for scraping, processing, and storing Umphrey’s McGee (UM) setlist, song, and venue data from allthings.umphreys.com.

## Directory Structure

- **UM/**: Main Python package for scraping and data management.
- **Data Output**: All processed data is saved to `../../3 - Data/UM/AllThingsUM/`.

## Modules Overview

### 1. `main.py`
- **Purpose**: Orchestrates the entire UM data pipeline.
- **Workflow**:
  1. Scrapes song catalog (`scrape_songs.py`)
  2. Scrapes venue data (`scrape_shows.py`)
  3. Scrapes setlists for all shows (`scrape_setlists.py`) (optional, can be slow)
  4. Saves all outputs to disk (`save_data.py`)
- **Logging**: Provides detailed logs for each step.

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
- **Functions**: `scrape_um_setlist_data`, `get_setlist_from_url`, `load_existing_data`, `get_last_update_time`, `update_um_data`
- **Purpose**: 
  - `scrape_um_setlist_data`: Scrapes setlist data for all songs and shows.
  - `get_setlist_from_url`: Scrapes setlist for a specific show.
  - `load_existing_data`: Loads existing data from disk.
  - `update_um_data`: Updates all data and saves it.
  - `get_last_update_time`: Reads the last update timestamp.
- **Outputs**: DataFrame with detailed setlist information for each show.

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

Run `main.py` to execute the full scraping and data-saving process. All required dependencies are standard (requests, pandas, BeautifulSoup, etc.). Use the `--update-setlists` flag to force a full setlist scrape (can be slow).
