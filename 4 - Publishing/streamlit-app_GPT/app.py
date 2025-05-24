"""
Streamlit app to publish band song prediction data from the predictions folders within each band folder in 3 - Data.

Features:
- Dynamic band selection
- Loads and displays prediction CSVs for each band
- Responsive, modern UI

Author: GPT-4
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

# --- CONFIG ---
BANDS_DIR = Path("../../3 - Data")
BAND_DISPLAY_NAMES = {
    "Goose": "Goose",
    "Phish": "Phish",
    "UM": "Umphrey's McGee",
    "WSP": "Widespread Panic"
}

st.set_page_config(
    page_title="Jam Band Nerd",
    page_icon="🎶",
    layout="wide"
)

st.markdown("<h1 style='text-align: center;'>Jam Band Nerd</h1>", unsafe_allow_html=True)

# --- UTILS ---
def list_band_folders(bands_dir: Path) -> List[str]:
    """List band folders in the data directory.

    Args:
        bands_dir (Path): Path to the data directory.
    Returns:
        List[str]: List of band folder names.
    """
    return [f.name for f in bands_dir.iterdir() if f.is_dir()]

def get_prediction_file_map(band_dir: Path) -> Dict[str, Path]:
    """Return a map of canonical labels ('CK+', 'Notebook') to file paths if present for the band.

    Args:
        band_dir (Path): Path to the band directory.
    Returns:
        Dict[str, Path]: {'CK+': path, 'Notebook': path}
    """
    predictions_dir = band_dir / "Predictions"
    file_map = {}
    if predictions_dir.exists():
        for f in predictions_dir.glob("*.csv"):
            fname = f.name.lower()
            if "ck+" in fname:
                file_map["CK+"] = f
            elif "notebook" in fname:
                file_map["Notebook"] = f
    return file_map

NOTEBOOK_LABELS = {
    "Phish": "Trey's Notebook",
    "WSP": "JoJo's Notebook",
    "Goose": "Rick's Notebook",
    "UM": "Joel's Notebook"
}


def load_prediction_csv(csv_path: Path) -> pd.DataFrame:
    """Load a prediction CSV as a DataFrame.

    Args:
        csv_path (Path): Path to CSV file.
    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"Failed to load {csv_path.name}: {e}")
        return pd.DataFrame()

# --- MAIN APP ---
band_folders = sorted(list_band_folders(BANDS_DIR))
band = st.sidebar.selectbox("Select Band", band_folders, format_func=lambda x: BAND_DISPLAY_NAMES.get(x, x))

band_dir = BANDS_DIR / band
prediction_file_map = get_prediction_file_map(band_dir)

if not prediction_file_map:
    st.warning(f"No prediction data found for {band}.")
else:
    # Only show 'CK+' and 'Notebook' if present
    dropdown_options = sorted([lbl for lbl in ["CK+", "Notebook"] if lbl in prediction_file_map], reverse=True)
    file_label = st.sidebar.selectbox("Select Prediction File", dropdown_options)
    csv_path = prediction_file_map[file_label]
    df = load_prediction_csv(csv_path)
    df = df.head(50)  # Only publish up to 50 rows

    # Display label logic
    if file_label == "CK+":
        display_label = "CK+"
        # Only keep expected columns if present, then rename
        expected_columns_ck = [
            "song", "times_played", "ltp_date", "current_gap",
            "avg_gap", "gap_ratio", "gap_z_score", "ck+_score"
        ]
        display_columns_ck = [
            "Song", "Times Played Overall", "LTP Date", "Current Gap", "Avg Gap",
            "Gap Ratio", "Gap Zscore", "CK+ Score"
        ]
        # Only keep if present
        df = df[[col for col in expected_columns_ck if col in df.columns]]
        df.columns = display_columns_ck[:len(df.columns)]
        df.index = range(1, len(df) + 1)
        df.index.name = "Rank"
    elif file_label == "Notebook":
        display_label = NOTEBOOK_LABELS.get(band, "Notebook")
        if band == "WSP":
            expected_columns = ["song", "times_played_last_2years", "last_time_played_date", "current_show_gap", "average_gap", "median_gap"]
            notebook_columns = [
                "Song", "Times Played Last 2 Years", "LTP Date", "Current Gap", "Average Gap", "Median Gap"
            ]
        else:
            expected_columns = ["song", "times_played_last_year", "last_time_played_date", "current_show_gap", "average_gap", "median_gap"]
            notebook_columns = [
                "Song", "Times Played Last Year", "LTP Date", "Current Gap", "Average Gap", "Median Gap"
            ]
        df = df[[col for col in expected_columns if col in df.columns]]
        df.columns = notebook_columns[:len(df.columns)]
        df.index = range(1, len(df) + 1)
        df.index.name = "Rank"
    else:
        display_label = file_label
    st.markdown(
        f"<h3 style='text-align: center;'>{BAND_DISPLAY_NAMES.get(band, band)} — {display_label}</h3>",
        unsafe_allow_html=True
    )
    if not df.empty:
        # Increase height to 2.5x default (default is ~400px)
        st.dataframe(df, use_container_width=True, height=1000)
    else:
        st.info("No data to display.")

