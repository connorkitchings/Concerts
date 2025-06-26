# Notebook Song Prediction Pipeline

## Overview
The Notebook pipeline predicts which songs are most likely to be played at upcoming shows for multiple bands (Widespread Panic, Phish, Goose, UM) using a method inspired by the legendary "Trey's Notebook" from Phish.net. This approach emphasizes recent history and frequency, focusing on the most-played songs in the last two years while excluding songs played in the last three shows.

- **Bands Supported:** Widespread Panic (WSP), Phish, Goose, Umphrey's McGee (UM)
- **Prediction Method:** Notebook (Phish.net Trey's Notebook-inspired ranking)
- **Automation:** Batch run for all bands via `run_all.py`

---

## What is the Notebook Method?
The Notebook method is based on the system made famous by Phish.net's "Trey's Notebook." This method predicts setlists by identifying songs that are frequently played in the recent past, but have not been played in the last few shows. It is designed to capture the patterns that bands use when constructing setlists, favoring songs that are in "rotation" but not overplayed.

**Credit:** This method is directly inspired by Phish.net's Trey's Notebook and is adapted here for multiple bands.

**Key Features:**
- Considers a rolling two-year window of past shows
- Counts the number of times each song was played in that window
- Excludes songs played in the last three shows
- Ranks songs by how often they were played in the two-year window
- Provides additional stats (last played date, average/median gap, etc.) for context

---

## Folder Structure
```
src/jambandnerd/predictions/notebook_model/
│
├── [band]/                  # One subdirectory per band (phish, goose, wsp, um)
│   ├── data_loader.py       # Loads and merges setlist, show, and song data
│   ├── model.py             # Implements Notebook scoring method
│   ├── predict_today.py     # Runs prediction, saves output
│   └── __pycache__/         # Python cache (ignore)
├── run_all.py               # (Legacy) Runs all band Notebook predictions
├── logger.py                # Logging utility for file/console output
```

---

## Data Flow

### Input Data
Each band's pipeline reads from CSV files in `3 - Data/<Band>/EverydayCompanion/`:
- `setlistdata.csv`: Song-by-song setlist data for each show
- `showdata.csv`: Show-level data (dates, indices, links)
- `songdata.csv`: Master list of songs

### Output Data
- `todaysnotebook.csv`: Top song predictions for the next show, saved in `data/<band>/predictions/`
- Logging information is saved to `logs/notebook.log`
- `date_updated.json` is updated to track prediction refreshes

---

## How to Run

From the project root:
```bash
python src/jambandnerd/predictions/notebook_model/run_all.py
```
Or run a single band pipeline (see subdirectory for details).

---

## Script Descriptions

### run_all.py
Runs the Notebook prediction pipeline for all bands by invoking each band's `predict_today.py` script. Logs results and errors.

### logger.py
Provides a logger that writes to both `logs/notebook.log` and the console, ensuring consistent logging across all scripts.

### <Band>/data_loader.py
Loads and merges setlist, show, and song data into a single DataFrame, standardizing columns and removing non-song entries.

### <Band>/model.py
Implements the Notebook method. Computes per-song statistics (times played in last 2 years, last played, gap stats, etc.) and ranks songs by their recent play frequency, excluding those played in the last three shows.

### <Band>/predict_today.py
Main pipeline script. Loads data, applies the Notebook method, saves the top predictions, and updates the refresh date.

---

## How to Run

1. Ensure all required data files are present in `3 - Data/<Band>/EverydayCompanion/`.
2. Run all band pipelines:

```bash
python run_all.py
```

3. Outputs will be saved in each band's `Predictions` folder and logs in `logs/notebook.log`.

---

## Extending or Modifying
- To add a new band, duplicate one of the band folders and adjust data paths as needed.
- To change the scoring method, modify `model.py` in the relevant band folder.
- All scripts use type hints and Google-style docstrings for maintainability.

---

## Credit
The Notebook method is inspired by the legendary "Trey's Notebook" as described on Phish.net. This implementation adapts those principles for automated, multi-band prediction.

---

## Contact
For questions or contributions, contact Connor Kitchings.
