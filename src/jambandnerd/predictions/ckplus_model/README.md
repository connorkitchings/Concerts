# CK+ Song Prediction Pipeline

## Overview
The CK+ pipeline predicts which songs are most likely to be played at upcoming shows for multiple bands (Widespread Panic, Phish, Goose, UM). It uses a statistical, gap-based method to rank songs by their likelihood of being played, based on historical setlist data.

- **Bands Supported:** Widespread Panic (WSP), Phish, Goose, Umphrey's McGee (UM)
- **Prediction Method:** CK+ (gap-based statistical ranking)
- **Automation:** Batch run for all bands via `run_all.py`

---

## What is the CK+ Method?
The CK+ (Connor Kitchings Plus) method is a statistical approach that uses the history of song performances to estimate which songs are "due" to be played. It is based on the idea that each song has a characteristic gap (number of shows) between performances. The method calculates how overdue a song is by comparing the current gap since it was last played to its historical average or median gap, and normalizes this with a z-score. The higher the CK+ score, the more likely the song is to be played next.

**Key Features:**
- Calculates the number of shows since each song's last performance (current gap)
- Computes average, median, and standard deviation of gaps between performances for each song
- Calculates gap ratio (current gap / average or median gap)
- Computes a z-score to normalize the gap ratio
- Ranks songs by a composite CK+ score
- Filters out songs that are rarely played or have been shelved for long periods

---

## Folder Structure
```
src/jambandnerd/predictions/ckplus_model/
│
├── [band]/                  # One subdirectory per band (phish, goose, wsp, um)
│   ├── data_loader.py       # Loads and merges setlist, show, and song data
│   ├── model.py             # Implements CK+ scoring method
│   ├── predict_today.py     # Runs prediction, saves output
│   └── __pycache__/         # Python cache (ignore)
├── run_all.py               # (Legacy) Runs all band CK+ predictions
├── logger.py                # Logging utility for file/console output
└── __pycache__/         # Python cache (ignore)
```

---

## Orchestration
- To run all CK+ predictions for all bands, use the orchestration script:
  ```bash
  python scripts/run_all_predict_todays.py
  ```
- This will run all `predict_today.py` scripts for each band.

---

## CI/CD
- Predictions are run nightly via GitHub Actions using the orchestration script.
- Outputs are saved to `data/[band]/generated/`.

---

## Data Flow

### Input Data
Each band's pipeline reads from CSV files in `3 - Data/<Band>/EverydayCompanion/`:
- `setlistdata.csv`: Song-by-song setlist data for each show
- `showdata.csv`: Show-level data (dates, indices, links)
- `songdata.csv`: Master list of songs

### Output Data
- `todaysck+.csv`: Top song predictions for the next show, saved in `data/<band>/predictions/`
- Logging information is saved to `logs/ckplus.log`
- `date_updated.json` is updated to track prediction refreshes

---

## How to Run

From the project root:
```bash
python src/jambandnerd/predictions/ckplus_model/run_all.py
```
Or run a single band pipeline (see subdirectory for details).

---

## Script Descriptions

### run_all.py
Runs the CK+ prediction pipeline for all bands by invoking each band's `predict_today.py` script. Logs results and errors.

### logger.py
Provides a logger that writes to both `logs/ck+.log` and the console, ensuring consistent logging across all scripts.

### <Band>/data_loader.py
Loads and merges setlist, show, and song data into a single DataFrame, standardizing columns and removing non-song entries.

### <Band>/model.py
Implements the CK+ method. Computes per-song statistics (times played, last played, gap stats, CK+ score) and ranks songs by their likelihood of being played next.

### <Band>/predict_today.py
Main pipeline script. Loads data, applies the CK+ method, saves the top predictions, and updates the refresh date.

---

## How to Run

1. Ensure all required data files are present in `3 - Data/<Band>/EverydayCompanion/`.
2. Run all band pipelines:

```bash
python run_all.py
```

3. Outputs will be saved in each band's `Predictions` folder and logs in `logs/ck+.log`.

---

## Extending or Modifying
- To add a new band, duplicate one of the band folders and adjust data paths as needed.
- To change the scoring method, modify `model.py` in the relevant band folder.
- All scripts use type hints and Google-style docstrings for maintainability.

---

## Contact
For questions or contributions, contact Connor Kitchings.
