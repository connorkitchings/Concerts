# WSP Setlist Creation Pipeline

This directory contains the code and data pipeline for scraping, processing, and storing Widespread Panic (WSP) setlist, show, and song data from everydaycompanion.com.

---

## Key Features
- **Centralized Configuration**: All paths, filenames, URLs, and settings are managed in `config.py` and can be overridden with environment variables.
- **Environment Variable Support**: Easily adjust data directories, log locations, and scrape parameters without code changes.
- **Consistent Naming**: Scripts and outputs are named to match the UM pipeline (`run_pipeline.py`, `export_data.py`, etc.).
- **Type Hints & Docstrings**: All Python functions and classes include type hints and Google-style docstrings for clarity and maintainability.
- **Modular Logging**: Each band uses its own `logger.py`, wrapping a shared general logger utility. Logs are always written to the correct, config-driven location for that band, as set in `config.py`. This prevents cross-band log contamination and makes the logging system robust and easy to maintain.

---

## Directory Structure
- **WSP/**: Main Python package for scraping and data management.
- **Data Output**: All processed data is saved to a config-driven directory (default: `../../3 - Data/WSP/EverydayCompanion/`).

---

## Logging System

Each band (WSP, Goose, UM, Phish) has its own `logger.py` that wraps a shared general logger utility. The logger is always configured using the band's `config.py` settings (`LOG_FILE`, `LOG_LEVEL`, etc.), ensuring that logs are written to the correct location and never overlap with other bands. To change log location or settings, update the environment variables or the appropriate `config.py`.

## Configuration & Environment Variables

All configuration is centralized in `WSP/config.py`. You can override any setting with environment variables:

| Variable                  | Purpose                                 | Example Value                        |
|---------------------------|-----------------------------------------|--------------------------------------|
| `WSP_DATA_DIR`            | Output data directory                   | `../../3 - Data/WSP/EverydayCompanion/` |
| `WSP_LOG_DIR`             | Log file directory                      | `../../logs/Setlist_Creation/WSP/`   |
| `WSP_BAND_NAME`           | Band name for logs/data                 | `WSP`                                |
| `WSP_SCRAPE_YEARS`        | Years to scrape (comma-separated)       | `1986,1987,1988,...`                 |
| `WSP_SKIP_YEARS`          | Years to skip (comma-separated)         | `2004`                               |
| `WSP_DATE_FORMAT`         | Date string format                      | `%m/%d/%Y`                           |
| `WSP_FOOTNOTE_PATTERN`    | Regex for footnotes                     | `\[(.*?)\]`                         |

---

## Modules Overview

### 1. `run_pipeline.py`
- **Purpose**: Orchestrates the entire WSP data pipeline.
- **Workflow**:
  1. Scrapes show metadata (`scrape_shows.py`)
  2. Scrapes song catalog (`scrape_songs.py`)
  3. Scrapes setlists for all shows (`scrape_setlists.py`)
  4. Saves all outputs to disk (`export_data.py`)
- **Logging**: Provides detailed logs for each step.

### 2. `scrape_shows.py`
- **Function**: `scrape_wsp_shows`
- **Purpose**: Scrapes and returns show metadata for all years (except skipped years) from everydaycompanion.com.
- **Outputs**: DataFrame with show dates, venues, cities, states, and links to setlists.

### 3. `scrape_songs.py`
- **Function**: `scrape_wsp_songs`
- **Purpose**: Scrapes the WSP song catalog from everydaycompanion.com.
- **Outputs**: DataFrame with song metadata.

### 4. `scrape_setlists.py`
- **Functions**: `get_setlist_from_link`, `load_setlist_data`
- **Purpose**: 
  - `get_setlist_from_link`: Scrapes and parses the setlist for a given show link.
  - `load_setlist_data`: Loads setlist data for a list of show links, merging new and existing data.
- **Outputs**: DataFrame with detailed setlist information for each show.

### 5. `export_data.py`
- **Function**: `save_wsp_data`
- **Purpose**: Saves the processed DataFrames to CSV files in the data directory. Also writes:
  - `last_updated.json`: Timestamp of last data update.
  - `next_show.json`: Metadata for the next upcoming show.
- **Files Created**: `songdata.csv`, `showdata.csv`, `setlistdata.csv`, `last_updated.json`, `next_show.json`.

### 6. `utils.py`
- **Functions**: 
  - `get_date_and_time`: Returns the current date and time as a string.
  - `date_format_for_all`: Standardizes date formats.
  - `print_relative_path`: Prints a path relative to the `Concerts/` directory.

---

## Data Outputs

All data is stored in the configured data directory (default: `3 - Data/WSP/EverydayCompanion/`):

| File                | Description                                                               |
|---------------------|---------------------------------------------------------------------------|
| `songdata.csv`      | Song catalog: song name, code, first/last played dates, play counts, aka. |
| `showdata.csv`      | Show metadata: date, venue, city, state, indices, setlist link.           |
| `setlistdata.csv`   | Song-by-song setlist data for each show (very large file).                |
| `last_updated.json` | Timestamp of the most recent pipeline run.                                |
| `next_show.json`    | Metadata for the next scheduled WSP show.                                 |

---

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
- All code is fully type-annotated and documented with Google-style docstrings.

---

## Running the Pipeline

Run `run_pipeline.py` to execute the full scraping and data-saving process:

```bash
python3 run_pipeline.py
```

All required dependencies are standard (requests, pandas, BeautifulSoup, etc.).

---

## Contributing & Code Style
- All Python code must use type hints for all functions and variables.
- All functions and classes must include Google-style docstrings.
- Configuration should always be sourced from `config.py` and/or environment variables.

---

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
