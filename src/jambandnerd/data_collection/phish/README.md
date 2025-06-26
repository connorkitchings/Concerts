# Phish Data Collection Pipeline

## Overview

This module collects, processes, and exports comprehensive setlist, show, venue, and song data for Phish. It integrates data from the phish.net API and web scraping to provide a canonical dataset for downstream analytics and applications.

- **API key required**: `PHISH_API_KEY` must be set in a `.env` file at the project root.
- **Automated ETL**: Orchestrated via a single pipeline script.
- **Outputs**: CSV and JSON files for analytics, ML, and dashboards.

## Data Sources

- **phish.net API (v5):** Song, show, and setlist data (requires API key).
- **phish.net website:** Additional song metadata via HTML table scraping.

## Directory Structure

```text
phish/
├── call_api.py         # API key loading and API request utilities
├── export_data.py      # Data export (CSV/JSON)
├── loaders.py          # Data loading and merging
├── run_pipeline.py     # Pipeline orchestrator (main entrypoint)
├── utils.py            # Logging helpers
├── README.md           # This file
```

## Pipeline Flow

1. **Data Acquisition:** Fetches song, show, and setlist data from the API and website.
2. **Data Processing:** Cleans, merges, and standardizes data using pandas.
3. **Data Export:** Saves as CSVs (`songdata.csv`, `showdata.csv`, `venuedata.csv`, `setlistdata.csv`, `transitiondata.csv`) and JSONs (`last_updated.json`, `next_show.json`).
4. **Logging:** Logs all steps and errors to `logs/Phish/phish_pipeline.log` and the console.

## Output Files

All outputs are saved to `data/phish/collected/` (relative to project root):

- `songdata.csv`         — Song-level data
- `showdata.csv`         — Show-level data
- `venuedata.csv`        — Venue-level data
- `setlistdata.csv`      — Setlist-level data
- `transitiondata.csv`   — Song transition data
- `last_updated.json`    — Timestamp of last successful run
- `next_show.json`       — Info for the next scheduled show (if available)

## Logging

- Log file: `logs/Phish/phish_pipeline.log`
- Format: `[MM-DD-YYYY HH:MM:SS] LEVEL: message`
- All major steps, errors, and completion messages are logged.

## Setup & Usage

1. **Create a `.env` file** in the project root (e.g., `/Users/connorkitchings/Desktop/Repositories/JamBandNerd/.env`) with your API key:

   ```env
   PHISH_API_KEY=your_phishnet_api_key_here
   ```

2. **Install dependencies** (from project root):

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the pipeline** (from the `phish` directory):

   ```bash
   python run_pipeline.py
   ```

   All outputs will be saved to the appropriate data and logs directories.

## Troubleshooting

- If you see errors about missing API key, ensure your `.env` file exists and contains a valid `PHISH_API_KEY`.
- If you see errors about missing directories, ensure the `data/phish/collected/` and `logs/Phish/` folders exist or are writable.
- All errors and stack traces are logged in `logs/Phish/phish_pipeline.log`.

## Project Standards

This module follows Windsurf/Cascade data science project guidelines for structure, code quality, and documentation. For more details, see the project root `README.md` and `.github/` docs.

## Dependencies

All dependencies are managed in the main `requirements.txt` file in the project root.
