# WSP Song Prediction Module

This directory contains the modules for aggregating features and generating song predictions for Widespread Panic (WSP) shows, using the data from the Everyday Companion archive.

## Directory Structure

- `data_loader.py` — Loads and merges setlist, show, and song data for WSP. **Excludes 'JAM' and 'DRUMS' from all calculations.**
- `model.py` — Aggregates song-level features for prediction (e.g., times played in the last 2 years, last played date, gaps, etc.). Logs the last 3 shows used for exclusion. **After aggregation, songs played in the last 3 shows are excluded from the output.**
- `predict_today.py` — Script to generate feature aggregations for today's date and save results to the predictions folder (now located outside the EverydayCompanion folder).
- `README.md` — This documentation file.

## Data Locations

- **Input Data**: `../../../3 - Data/WSP/EverydayCompanion/`
  - `setlistdata.csv` — Song-by-song setlist data for each show
  - `showdata.csv` — Show metadata (date, venue, city, etc.)
  - `songdata.csv` — Song metadata (first played, last played, etc.)
- **Predictions Output**: `../../../3 - Data/WSP/Predictions/`
  - `todaysnotebook.csv` — Aggregated features for all songs as of today

## Feature Aggregation and Exclusion Logic
- The aggregation window is **1 year**. All features such as times played are calculated for the 1-year period before (but not including) the target show date.
- The output column is named `times_played_last_year`.
- For determining the "last 3 shows" exclusion, only shows **before** the target show date are considered (future and today are excluded).
- **After feature aggregation, any song played in the last 3 shows is excluded from the final output.**
- **The last 3 shows used for exclusion are logged for transparency (see logs/Notebook/notebook.log).**
- **'JAM' and 'DRUMS' are fully excluded from all calculations.**

## Usage

To generate today's feature aggregation:

```bash
python predict_today.py
```

The output will be saved to the predictions folder as `todaysnotebook.csv`.

### Historical Evaluation

To evaluate prediction accuracy over the last N shows (default 50) for both top 25 and top 50 predictions:

```bash
python historical_testing.py --num_shows 50
```

This will generate a single JSON file:
```
../../../3 - Data/WSP/Predictions/notebook/notebook_accuracy.json
```
with the following structure:

```json
{
  "top_25": {
    "most_recent_shows": 50,
    "overall_accuracy": <float>,
    "results": [
      {"showid": ..., "showdate": ..., "accuracy": ...},
      ...
    ]
  },
  "top_50": {
    "most_recent_shows": 50,
    "overall_accuracy": <float>,
    "results": [ ... ]
  }
}
```
- Each `results` array is sorted by showdate descending (most recent first).
- `overall_accuracy` is the average per-show accuracy for that group.
- `most_recent_shows` is the number of shows evaluated in each group.

## Customization
- To predict for a different date, modify the `today` variable in `predict_today.py`.
- To integrate a machine learning model, use the output features as input to your model of choice (see Goose/Phish modules for examples).

## Requirements
- Python 3.8+
- pandas

## Notes
- The predictions folder should be located at the same level as the EverydayCompanion data folder, i.e.:

```
3 - Data/WSP/
    ├── EverydayCompanion/
    └── Predictions/
```

- All modules reference these locations relative to this structure.
