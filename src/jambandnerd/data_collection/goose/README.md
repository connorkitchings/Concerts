# Goose Data Collection Pipeline

## Overview
This module collects, processes, and exports comprehensive setlist, show, venue, and song data for Goose. Data is sourced from the elgoose.net API and website. Outputs are standardized for downstream analytics and ML.

## Overview

This module collects, processes, and exports comprehensive setlist, show, venue, and song data for the band Goose. It integrates data from the elgoose.net API and web scraping to provide a canonical dataset for downstream analytics and applications.

- **No API key required**: All data is public.
- **Automated ETL**: Orchestrated via a single pipeline script.
- **Outputs**: CSV and JSON files for easy use in analytics, ML, and dashboards.

## Data Sources

- **elgoose.net API (v1/v2):** Song, show, and setlist data.
- **elgoose.net website:** Additional song metadata via HTML table scraping.

## Directory Structure

```text
goose/
├── call_api.py         # API request utilities
├── export_data.py      # Data export (CSV/JSON)
├── loaders.py          # Data loading and merging
├── run_pipeline.py     # Pipeline orchestrator (main entrypoint)
├── utils.py            # Logging, paths, time helpers
├── README.md           # This file
```

## Pipeline Flow

1. **Data Acquisition:** Fetches song, show, and setlist data from the API and website.
2. **Data Processing:** Cleans, merges, and standardizes data using pandas.
3. **Data Export:** Saves as CSVs (`songdata.csv`, `showdata.csv`, `venuedata.csv`, `setlistdata.csv`, `transitiondata.csv`) and JSONs (`last_updated.json`, `next_show.json`).
4. **Logging:** Logs all steps and errors to `logs/Goose/goose_pipeline.log` and the console.

## Output Files

All outputs are saved to `data/goose/collected/` (relative to project root):

- `songdata.csv`         — Song-level data
- `showdata.csv`         — Show-level data
- `venuedata.csv`        — Venue-level data
- `setlistdata.csv`      — Setlist-level data
- `transitiondata.csv`   — Song transition data
- `last_updated.json`    — Timestamp of last successful run
- `next_show.json`       — Info for the next scheduled show (if available)

## Logging

- Log file: `logs/Goose/goose_pipeline.log`
- Format: `[MM-DD-YYYY HH:MM:SS] LEVEL: message`
- All major steps, errors, and completion messages are logged.

## Setup & Usage

1. **Install dependencies** (from project root):

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the pipeline** (from the `goose` directory):

   ```bash
   python run_pipeline.py
   ```

   All outputs will be saved to the appropriate data and logs directories.

## Troubleshooting

- If you see errors about missing directories, ensure the `data/goose/` and `logs/Goose/` folders exist or are writable.
- All errors and stack traces are logged in `logs/Goose/goose_pipeline.log`.
- No API key or .env file is required for Goose.

## Project Standards

This module follows Windsurf/Cascade data science project guidelines for structure, code quality, and documentation. For more details, see the project root `README.md` and `.github/` docs.

- The pipeline is modular and can be extended for additional data sources or analytics.
- Logging is provided for debugging and auditability.
- For questions or issues, please refer to the code comments or contact the maintainer.
