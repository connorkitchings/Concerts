"""Streamlit app to publish band song prediction data from the predictions folders within each band folder in 3 - Data.

Features:
- Dynamic band selection
- Loads and displays prediction CSVs for each band
- Responsive, modern UI

Author: GPT-4
"""
import streamlit as st
from pathlib import Path
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple

# Import constants and utility modules
from constants import BANDS_DIR, BAND_DISPLAY_NAMES
from band_utils import list_band_folders, get_prediction_file_map
from data_loader import load_prediction_csv, format_dataframe, get_column_config
from next_show_utils import get_next_show_info
from timestamp_utils import get_data_collection_timestamp, get_prediction_timestamp
from ui_components import display_method_explanation, display_disclaimer, display_next_show

def main() -> None:
    """Main application function."""
    # Configure the app
    st.set_page_config(
        page_title="Jam Band Nerd",
        page_icon="🎶",
        layout="wide"
    )

    st.markdown("<h1 style='text-align: center;'>Jam Band Nerd</h1>", unsafe_allow_html=True)

    # --- MAIN APP ---
    if not BANDS_DIR.exists():
        st.error(f"Data directory '{BANDS_DIR.resolve()}' not found. Please ensure your data is uploaded and the path is correct.")
        return
    band_folders = sorted(list_band_folders(BANDS_DIR))
    band = st.sidebar.selectbox("Select Band", band_folders, format_func=lambda x: BAND_DISPLAY_NAMES.get(x, x))

    band_dir = BANDS_DIR / band / "Generated"
    prediction_file_map = get_prediction_file_map(band_dir)

    if not prediction_file_map:
        st.warning(f"No prediction data found for {band}.")
        return

    # Show 'CK+', and 'Notebook' if present
    dropdown_options = sorted([lbl for lbl in ["CK+", "Notebook"] if lbl in prediction_file_map], reverse=True)
    file_label = st.sidebar.selectbox("Select Prediction Method", dropdown_options)
    
    # Display method explanation
    display_method_explanation(file_label)

    # --- Prediction Data Loading ---
    try:
        csv_path = prediction_file_map[file_label]
        df = load_prediction_csv(csv_path)
        df = df.head(50)  # Only publish up to 50 rows
    except Exception as e:
        st.error(f"Error loading prediction data: {str(e)}")
        df = None
    
    if df is not None and not df.empty:
        # Get column configuration and format dataframe
        display_label, expected_columns, display_columns = get_column_config(file_label, band)
        df = format_dataframe(df, expected_columns, display_columns)
        
        # Display header with band and method
        st.markdown(
            f"<h3 style='text-align: center;'>{BAND_DISPLAY_NAMES.get(band, band)} — {display_label}</h3>",
            unsafe_allow_html=True
        )
        
        # Get and display next show information
        next_show_str = get_next_show_info(band, BANDS_DIR)
        display_next_show(next_show_str)
        
        # Display the dataframe
        st.dataframe(df, use_container_width=True, height=1000)
        
        # Get timestamps and display disclaimer
        data_date_str, data_time_str = get_data_collection_timestamp(band, band_dir)
        pred_date_str, pred_time_str = get_prediction_timestamp(band_dir, file_label)
        display_disclaimer(pred_date_str, pred_time_str, data_date_str, data_time_str)
    else:
        st.info("No data to display.")

# Run the main application
if __name__ == "__main__":
    main()
