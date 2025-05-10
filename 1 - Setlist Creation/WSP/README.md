# WSP Setlist Creation Pipeline

This directory contains the code and data pipeline for scraping, processing, and storing Widespread Panic (WSP) setlist, show, and song data from everydaycompanion.com.

## Directory Structure

- **WSP/**: Main Python package for scraping and data management.
- **Data Output**: All processed data is saved to `../../3 - Data/WSP/EverydayCompanion/`.

## Modules Overview

### 1. `main.py`
- **Purpose**: Orchestrates the entire WSP data pipeline.
- **Workflow**:
  1. Scrapes show metadata (`scrape_shows.py`)
  2. Scrapes song catalog (`scrape_songs.py`)
  3. Scrapes setlists for all shows (`scrape_setlists.py`)
  4. Saves all outputs to disk (`save_data.py`)
- **Logging**: Provides detailed logs for each step.

### 2. `scrape_shows.py`
- **Function**: `scrape_wsp_shows`
- **Purpose**: Scrapes and returns show metadata for all years (except skipped years) from everydaycompanion.com.
- **Outputs**: DataFrame with show dates, venues, cities, states, and links to setlists.
- **Key Columns**: `date`, `venue`, `city`, `state`, `link`, and several index columns.

### 3. `scrape_songs.py`
- **Function**: `scrape_wsp_songs`
- **Purpose**: Scrapes the WSP song catalog from everydaycompanion.com.
- **Outputs**: DataFrame with song metadata.
- **Key Columns**: `song`, `code`, `ftp` (first played), `ltp` (last played), `times_played`, `aka` (also known as).

### 4. `scrape_setlists.py`
- **Functions**: `get_setlist_from_link`, `load_setlist_data`
- **Purpose**: 
  - `get_setlist_from_link`: Scrapes and parses the setlist for a given show link.
  - `load_setlist_data`: Loads setlist data for a list of show links, merging new and existing data.
- **Outputs**: DataFrame with detailed setlist information for each show.
- **Key Columns**: `song_name`, `set`, `song_index_set`, `song_index_show`, `into`, `song_note_detail`, `link`.

### 5. `save_data.py`
- **Function**: `save_wsp_data`
- **Purpose**: Saves the processed DataFrames to CSV files in the data directory. Also writes:
  - `last_updated.json`: Timestamp of last data update.
  - `next_show.json`: Metadata for the next upcoming show.
- **Files Created**: `songdata.csv`, `showdata.csv`, `setlistdata.csv`, `last_updated.json`, `next_show.json`.

### 6. `utils.py`
- **Functions**: 
  - `get_data_dir`: Returns the path to the data directory.
  - `get_date_and_time`: Returns the current date and time as a string.
  - `date_format_for_all`: Standardizes date formats.

---

## Data Outputs

All data is stored in `3 - Data/WSP/EverydayCompanion/`:

| File                | Description                                                               |
|---------------------|---------------------------------------------------------------------------|
| `songdata.csv`      | Song catalog: song name, code, first/last played dates, play counts, aka. |
| `showdata.csv`      | Show metadata: date, venue, city, state, indices, setlist link.           |
| `setlistdata.csv`   | Song-by-song setlist data for each show (very large file).                |
| `last_updated.json` | Timestamp of the most recent pipeline run.                                |
| `next_show.json`    | Metadata for the next scheduled WSP show.                                 |

### Example: `songdata.csv` Columns

- `song`: Name of the song
- `code`: Unique code for the song
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

---

## Pipeline Context

- The pipeline is designed for reproducibility and automated updates.
- Data is scraped directly from everydaycompanion.com, ensuring up-to-date information.
- All modules are highly modular, allowing for extension or adaptation to other bands or sources.

---

## Running the Pipeline

Run `main.py` to execute the full scraping and data-saving process. All required dependencies are standard (requests, pandas, BeautifulSoup, etc.).
