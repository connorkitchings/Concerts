# Making_Predictions Directory Overview

This document outlines the purpose and data flow of all major files in the `Making_Predictions` directory, as well as the structure of the data they create and use.

---

## 1. `PredictionMaker.py`
- **Purpose:**
  - Defines an abstract base class (`PredictionMaker`) for all band-specific setlist prediction makers.
  - Standardizes the interface for loading data, transforming it, making predictions, and saving results.
  - Provides a `PredictionMakerManager` class to register and manage multiple band predictors.
- **Data Handled/Created:**
  - No direct data creation, but sets up expected methods for subclasses (e.g., `load_data`, `create_ckplus`, `create_notebook`, `create_and_save_predictions`).

---

## 2. Band-Specific Predictors
- **Files:** `Goose.py`, `Phish.py`, `WSP.py`, `UM.py`
- **Purpose:**
  - Each file contains a subclass of `PredictionMaker` tailored to a specific band (Goose, Phish, WSP, UM).
  - Implements band-specific logic for loading, cleaning, and merging setlist and song data.
  - Prepares the data for making predictions about future setlists.
- **Data Handled/Created:**
  - **Loads the following CSVs (created by the Setlist Collector):**
    - `songdata.csv`: Metadata for every song performed (e.g., song name, original artist, debut date, play counts).
    - `venuedata.csv`: Metadata for venues (e.g., venue name, city, state, country).
    - `showdata.csv`: Details for every concert (e.g., show date, venue, tour, show number).
    - `setlistdata.csv`: Detailed setlist information for each show (e.g., song order, transitions, notes).
    - `transitiondata.csv`: Data on transitions between songs (if available).
  - **Creates:**
    - In-memory pandas DataFrames for each CSV, used for analytics and prediction.
    - Processed/filtered DataFrames (e.g., `setlist_by_song`) that merge setlist and show data for analysis.
    - Prediction output files (typically saved in `Data/{Band}/Predictions/`) containing predicted setlists or statistics.
- **Band-specific Notes:**
  - `GoosePredictionMaker`: Loads all collector CSVs, merges and processes them for setlist predictions for Goose.
  - `PhishPredictionMaker`: Similar to Goose, but may filter out shows marked as excluded from stats.
  - `WSPPredictionMaker`: Loads and processes collector CSVs, with logic to remove reprises and sort setlists efficiently.
  - `UMPredictionMaker`: Loads and processes collector CSVs, standardizing song names and handling show indices.

---

## 3. `Make_Predictions.py`
- **Purpose:**
  - Main script to orchestrate the prediction process for all bands.
  - Registers each band’s prediction class with the manager and runs the prediction workflow for all.
- **Data Handled/Created:**
  - Instantiates and manages all band predictors.
  - Executes the prediction process for each band.
  - Triggers the creation of prediction output files for each band, typically saved in `Data/{Band}/Predictions/`.

---

# Data Created by the Pipeline

- **songdata.csv:**
  - Song-level metadata (ID, name, original artist, debut date, play count, etc.)
- **showdata.csv:**
  - Show-level metadata (ID, date, venue, tour, show number, etc.)
- **venuedata.csv:**
  - Venue-level metadata (ID, name, city, state, country, etc.)
- **setlistdata.csv:**
  - Song-by-song setlist details for each show (song name, order, transitions, notes, etc.)
- **transitiondata.csv:**
  - Details about transitions and segues between songs (if available).
- **Prediction Output Files:**
  - Band-specific prediction results, such as predicted setlists or statistical analyses, saved in `Data/{Band}/Predictions/`.

---

# Summary

- The `Making_Predictions` system efficiently loads, processes, and analyzes collector-generated datasets for each band.
- It produces high-quality, analysis-ready data and predictions for setlists, using a modular, extensible architecture.
- All data flows from the collector’s output CSVs through standardized predictors and is ultimately used to generate actionable prediction outputs.
