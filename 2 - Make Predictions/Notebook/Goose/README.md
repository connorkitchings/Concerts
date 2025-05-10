# Goose Song Prediction Notebook

This directory contains scripts and utilities for predicting which songs are likely to be played at upcoming Goose concerts, using setlist history and show metadata.

## Directory Structure

- `predict_today.py` — **Main script to generate song predictions for today or a specified date. This is the only script that should be run directly.**
- `model.py` — Internal module for feature engineering and aggregation logic.
- `data_loader.py` — Internal module for data loading and merging utilities.
- `logger.py` — Shared logger for all scripts in this folder. Logs to `../../logs/Notebook/notebook.log`.

## Data Requirements

This code expects the following CSV files to exist (relative to this directory):

- `../../../3 - Data/Goose/ElGoose/setlistdata.csv` — Setlist data (song-by-show)
- `../../../3 - Data/Goose/ElGoose/showdata.csv` — Show metadata (dates, venues)
- `../../../3 - Data/Goose/ElGoose/songdata.csv` — Song metadata
- Output will be saved to: `../../../3 - Data/Goose/Predictions/todaysnotebook.csv`

## Feature Aggregation and Exclusion Logic
- The aggregation window is **1 year**. All features such as times played are calculated for the 1-year period before (but not including) the target show date.
- The output column is named `times_played_last_year`.
- For determining the "last 3 shows" exclusion, only shows **before** the target show date are considered.
- After feature aggregation, any song played in the last 3 shows is excluded from the final output.
- The last 3 shows used for exclusion are logged for transparency (see logs/Notebook/notebook.log).

## Usage

1. Ensure all required CSV files are present in the correct locations (see above).
2. From this directory, run:

```bash
python predict_today.py
```

This will generate aggregated song features and predictions for today's date and save them to the output CSV.

### Logging

All scripts in this folder use a unified logger. Log messages are saved to:
```
../../logs/Notebook/notebook.log
```
You can monitor this file for info, warnings, and errors during processing. To add custom debug logs, use:
```python
from logger import get_logger
logger = get_logger(__name__)
logger.info("Your message")
```

## Customization

- To predict for a different date, modify the `today` variable in `predict_today.py`.
- To use different data sources, adjust the paths in `predict_today.py` accordingly.

## Dependencies

- Python 3.7+
- pandas

Install dependencies with:

```bash
pip install pandas
```

## Notes

- All scripts assume they are run from this (`Notebook`) directory.
- Feature engineering includes historical play counts, last time played, show gaps, and more (see `model.py`).

## Contact

For questions or issues, please contact the repository maintainer.
