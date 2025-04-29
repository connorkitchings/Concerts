# Setlist Data Processing for Widespread Panic

## 1. Libraries Loaded
- **Data Handling**: `tidyverse`, `rvest`, `lubridate`, `purrr`
- **Modeling**: `xgboost`, `caret`, `pROC`, `Metrics`, `performanceEstimation`
- **Plotting**: `ggplot2`, `gt`, `paletteer`

---

## 2. Define Load + Clean Functions

### a) Process Dimensional Tour Data (`process_dim()`)
- Scrape tour dates and venues from `everydaycompanion.com`.
- Handle missing or estimated dates.
- Generate direct setlist links for each show.
- Extract metadata: state, city, venue name.
- Flag shows that are radio performances.
- Create indexes:
  - `show_index`: show number across history.
  - `run_index`: consecutive run of shows.
  - `show_in_run`: order of show in run.

### b) Process Setlist for a Show (`process_setlist()`)
- Scrape and clean show setlists.
- Parse sets and songs.
- Separate main songs from notes and show notes.
- Handle multiple song segments (">" transitions).
- Clean weird characters and fix known song title issues.
- Return:
  - Songs table.
  - Notes table.
  - Show notes table.

---

## 3. Load All Show and Setlist Data (`load_all_data()`)
- Scrape all historical shows (1986 - today).
- Create split:
  - `show_dim`: historical shows.
  - `fut_dim`: upcoming future shows.
- Load setlists into a `songs` DataFrame.
- For each song:
  - Track set numbers.
  - Normalize set assignments.
  - Attach show-level notes.
- Combine song, show, and future data into final outputs.
- Outputs:
  - Song Fact Table.
  - Historical Show Table.
  - Future Show Table.

---

## 4. Update Most Recent Shows (`update_all_data()`)
- Check if any new shows have occurred since last data save.
- If yes:
  - Load only new shows and setlists.
  - Update historical song and show tables.
- If no:
  - Return existing saved data.
- Recombine all updated tables.

---

## 5. Create and Save Tables

### a) Song Fact Table
- All historical songs with metadata.

### b) Show Dimensional Table
- Historical + Future shows combined.
- Save `.rds` files:
  - `WSP_Song_Fact_Table_[start]_to_[end].rds`
  - `WSP_Show_Dim_Table_[start]_to_[end].rds`

---

# Summary
This script scrapes, cleans, builds, and updates complete Widespread Panic show and setlist data. It ensures:
- Missing dates and venues are corrected.
- Radio shows are flagged.
- Songs and notes are properly parsed and matched.
- Data is exportable for model building and analysis.

---

> **Website Source:** [Everyday Companion](http://everydaycompanion.com/)

