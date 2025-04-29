# Widespread Panic Model Building Process

## Preprocessing Steps

### 1. Load and Re-Index Shows
- Function: `prep_model_input(df, song_df)`
- Actions:
  - Filter out radio and soundcheck shows.
  - Reindex shows by date.
  - Create new `show_index`, `run_index`, and `show_in_run`.
  - Split into "future" shows (`dim_future`) and "historical" shows (`model_dim`).
  - Merge shows with setlists to create the `model_data` table.

### 2. Manipulate Data for Input Tables

#### a) Single Show Input Table
- Function: `manipulate_train(test_date)`
- Actions:
  - Create show-specific variables (location, state, venue).
  - Create summary statistics:
    - Total shows and runs in time windows (6 months, 1 year, etc.).
    - Shows/runs by location and weekday.
    - LTP (Last Time Played) metrics.
    - Song frequency and play percentages.
    - Difference metrics between recent and historical performance.
    - Eligibility flag for songs (>= 3 LTP values).
    - Metrics related to run and show scores.

#### b) Predict for the Next Show
- Apply `manipulate_train()` for the next scheduled show to create `sell_sell_table`.

#### c) Create Training Dataset
- Function: `create_train_set(end_date, train_n)`
- Actions:
  - For the most recent `n` shows:
    - Create song prediction tables.
    - Mark if the song was played.
    - Aggregate into `model_table`.

## Model Training

### 3. Train Model
- Function: `train_model(input, resample)`
- Actions:
  - Separate ID, feature, and target columns.
  - Optionally apply SMOTE resampling.
  - Train a basic XGBoost binary classifier (`xgb.DMatrix`).
  - Evaluate using log loss, accuracy, and AUC.
  - Plot accuracy across different thresholds.

- Two versions are trained:
  - `trained_xgb_resample` (with SMOTE)
  - `trained_xgb_raw` (without SMOTE)

## Model Application

### 4. Apply Model to Future Show
- Function: `apply_model(mdl, input)`
- Actions:
  - Predict song probabilities for a given show.
  - Return a table sorted by highest probability.

### 5. Create Prediction Tables
- Generate predictions for:
  - Single night shows (e.g., AC Night 1, 2, 3).
  - Full show runs by averaging nightly predictions.

## Table Building for Outputs

### 6. Build Prediction Tables for Visualization

#### a) Single Night Top Predictions
- Function: `build_next_show_table(data, n_preds)`
- Actions:
  - Select key columns.
  - Format and style with `gt()`.
  - Color metrics by strength and frequency.

#### b) Full Run Top Predictions
- Function: `build_next_run_table(data, n_preds)`
- Actions:
  - Display mean prediction scores across the full run.

#### c) Bust Out Predictions
- Function: `build_next_run_rare_table(data, n_preds)`
- Actions:
  - Filter songs:
    - LTP > 15 shows.
    - Played < 10% of shows since debut.
  - Highlight rare songs likely to be played.

---

# Summary
This process:
- Prepares and cleans concert data.
- Creates feature-rich input tables.
- Trains a predictive model.
- Applies the model to future shows.
- Produces highly customized, styled prediction tables for setlists.

---

> **Data Sources:**
> - `WSP_Show_Dim_Table_1986_to_2025.rds`
> - `WSP_Song_Fact_Table_1986_to_2025.rds`

