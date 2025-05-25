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
        elif band == "UM":
            expected_columns = ["song", "times_played_last_year", "last_time_played", "average_gap_days", "median_gap_days"]
            notebook_columns = ["Song", "Times Played Last Year", "LTP Date", "Average Gap", "Median Gap"]
            df = df[[col for col in expected_columns if col in df.columns]]
            df.columns = notebook_columns[:len(df.columns)]
            df.index = range(1, len(df) + 1)
            df.index.name = "Rank"
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

    # --- NEXT SHOW SUBHEADLINE ---
    # Try to load showdata.csv for this band
    # --- NEXT SHOW SUBHEADLINE (from next_show.json) ---
    import json
    from datetime import datetime
    next_show_json_paths = {
        "WSP": BANDS_DIR / "WSP" / "EverydayCompanion" / "next_show.json",
        "Phish": BANDS_DIR / "Phish" / "PhishNet" / "next_show.json",
        "Goose": BANDS_DIR / "Goose" / "ElGoose" / "next_show.json",
        "UM": BANDS_DIR / "UM" / "AllThingsUM" / "next_show.json",
    }
    next_show_path = next_show_json_paths.get(band)
    next_show_str = None
    def format_next_show_wsp(data: dict) -> str:
        """Format next show string for WSP using all available fields."""
        date = data.get("date")
        venue = data.get("venue")
        city = data.get("city")
        state = data.get("state")
        if date:
            try:
                date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
            except Exception:
                date_fmt = date
        else:
            date_fmt = None
        if date_fmt and venue and city and state and state != 'UU':
            return f"Next show: {date_fmt} at {venue} in {city}, {state}"
        elif date_fmt and venue and city:
            return f"Next show: {date_fmt} at {venue} in {city}"
        elif date_fmt and venue:
            return f"Next show: {date_fmt} at {venue}"
        elif date_fmt:
            return f"Next show: {date_fmt}"
        return None
    def format_next_show_um(data: dict) -> str:
        """Format next show string for UM using available fields."""
        venue = data.get("Venue Name")
        city = data.get("City")
        state = data.get("State")
        date = data.get("Last Played")  # No direct date, fallback to last played
        if date:
            try:
                date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
            except Exception:
                date_fmt = date
        else:
            date_fmt = None
        if date_fmt and venue and city and state:
            return f"Next show: {date_fmt} at {venue} in {city}, {state}"
        elif date_fmt and venue and city:
            return f"Next show: {date_fmt} at {venue} in {city}"
        elif date_fmt and venue:
            return f"Next show: {date_fmt} at {venue}"
        elif date_fmt:
            return f"Next show: {date_fmt}"
        return None
    def format_next_show_phish_goose(data: dict, showdata_path: Path, venuedata_path: Path, date_field: str = "show_date") -> str:
        """Format next show string for Phish and Goose using showdata.csv and venuedata.csv as lookup.

        Args:
            data (dict): Parsed next_show.json['next_show']
            showdata_path (Path): Path to showdata.csv
            venuedata_path (Path): Path to venuedata.csv
            date_field (str): Date field to use from JSON
        Returns:
            str: Formatted next show string, or None if not enough info
        """
        date = data.get(date_field) or data.get("showdate")
        # For Goose, next_show.json may have venue_id directly
        venue_id_json = data.get('venue_id') or data.get('venueid')
        if not date or not showdata_path.exists() or not venuedata_path.exists():
            # fallback to minimal
            if date:
                try:
                    date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
                except Exception:
                    date_fmt = date
                return f"Next show: {date_fmt}"
            return None
        try:
            show_df = pd.read_csv(showdata_path)
            venue_df = pd.read_csv(venuedata_path)
            # Try to find the show row by date, but if not found, fallback to venue_id from json
            date_cols = [col for col in show_df.columns if 'date' in col.lower()]
            found = None
            for dcol in date_cols:
                match = show_df[show_df[dcol] == date]
                if not match.empty:
                    found = match.iloc[0]
                    break
                # Try formatted
                try:
                    show_df[dcol] = pd.to_datetime(show_df[dcol], errors='coerce').dt.strftime('%Y-%m-%d')
                    match = show_df[show_df[dcol] == date]
                    if not match.empty:
                        found = match.iloc[0]
                        break
                except Exception:
                    continue
            # If not found by date, try by venue_id from JSON (Goose case)
            if found is None and venue_id_json is not None:
                venue_id_json_str = str(venue_id_json)
                # Try to find the most recent or matching show for this venue_id
                venue_id_cols = [col for col in show_df.columns if 'venue_id' in col.lower() or 'venueid' in col.lower()]
                for vcol in venue_id_cols:
                    match = show_df[show_df[vcol].astype(str) == venue_id_json_str]
                    if not match.empty:
                        found = match.sort_values(by=date_cols[0] if date_cols else vcol, ascending=False).iloc[0]
                        break
            try:
                date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
            except Exception:
                date_fmt = date
            venue, city, state = None, None, None
            venue_id = None
            if found is not None:
                venue_id = found.get('venueid') or found.get('venue_id') or venue_id_json
            else:
                venue_id = venue_id_json
            # Venue lookup
            if venue_id is not None:
                venue_id_str = str(venue_id)
                venue_matches = venue_df[(venue_df['venue_id'].astype(str) == venue_id_str) | (venue_df.get('venueid', pd.Series()).astype(str) == venue_id_str)]
                if not venue_matches.empty:
                    vrow = venue_matches.iloc[0]
                    venue = vrow.get('venue') or vrow.get('venuename')
                    city = vrow.get('city')
                    state = vrow.get('state')
            # Fallback to any venue/city/state directly in show row
            if found is not None:
                venue = venue or found.get('venue') or found.get('Venue Name') or found.get('venue_name')
                city = city or found.get('city') or found.get('City')
                state = state or found.get('state') or found.get('State')
            if date_fmt and venue and city and state:
                return f"Next show: {date_fmt} at {venue} in {city}, {state}"
            elif date_fmt and venue and city:
                return f"Next show: {date_fmt} at {venue} in {city}"
            elif date_fmt and venue:
                return f"Next show: {date_fmt} at {venue}"
            elif date_fmt:
                return f"Next show: {date_fmt}"
            return None
        except Exception:
            try:
                date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
            except Exception:
                date_fmt = date
            return f"Next show: {date_fmt}"
        return None
    if next_show_path and next_show_path.exists():
        try:
            with open(next_show_path, "r") as f:
                js = json.load(f)
            data = js.get("next_show", {})
            if band == "WSP":
                next_show_str = format_next_show_wsp(data)
            elif band == "UM":
                next_show_str = format_next_show_um(data)
            elif band == "Goose":
                showdata_path = BANDS_DIR / "Goose" / "ElGoose" / "showdata.csv"
                venuedata_path = BANDS_DIR / "Goose" / "ElGoose" / "venuedata.csv"
                next_show_str = format_next_show_phish_goose(data, showdata_path, venuedata_path, date_field="show_date")
            elif band == "Phish":
                showdata_path = BANDS_DIR / "Phish" / "PhishNet" / "showdata.csv"
                venuedata_path = BANDS_DIR / "Phish" / "PhishNet" / "venuedata.csv"
                next_show_str = format_next_show_phish_goose(data, showdata_path, venuedata_path, date_field="showdate")
        except Exception as e:
            next_show_str = None
    if next_show_str:
        st.markdown(f"<h4 style='text-align: center; color: #666;'>{next_show_str}</h4>", unsafe_allow_html=True)
    
    if not df.empty:
        # Increase height to 2.5x default (default is ~400px)
        st.dataframe(df, use_container_width=True, height=1000)
    else:
        st.info("No data to display.")

