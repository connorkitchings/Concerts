import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_option_menu import option_menu
from PIL import Image
import datetime
from stream_utils import get_last_updated_times, get_next_show_info

# Define base directory and bands
base_url = "https://raw.githubusercontent.com/connorkitchings/Concerts/main/"
bands = ["Goose", "Phish", "UM", "WSP"]
band_names = {"Goose": "Goose", "Phish": "Phish", "UM": "Umphrey's McGee", "WSP": "Widespread Panic"}
band_notebooks = {"Goose": "Rick's", "Phish": "Trey's", "UM": "Joel's", "WSP": "JoJo's"}

# --- CONFIGS ---
st.set_page_config(
    page_title="Jam Band Nerd Demo",
    page_icon="🎸",  # Added a guitar emoji as page icon
    layout="wide"
)

# Center header and image
st.markdown("<h1 style='text-align: center;'>Jam Band Nerd</h1>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://hevria.com/wp-content/uploads/2015/07/GD-rainbow2-1024x770.jpg")

# --- LOAD DATA ---
@st.cache_data
def load_data(band):
    """Load the notebook and CK+ data for a specific band"""
    try:
        notebook_url = f"{base_url}Data/{band}/Predictions/notebook.csv"
        ckplus_url = f"{base_url}Data/{band}/Predictions/ck_plus.csv"
        data_notebook = pd.read_csv(notebook_url)
        data_notebook.columns = ["Song", "Times Played in Last Year", "Last Time Played", "Current Gap", "Average Gap", "Median Gap"]
        data_ckplus = pd.read_csv(ckplus_url)
        return data_notebook.head(50), data_ckplus.head(50)
    except FileNotFoundError:
        st.error(f"Data files for {band} not found. Please check your file paths.")
        return pd.DataFrame(), pd.DataFrame()
    except pd.errors.EmptyDataError:
        st.error(f"Data files for {band} are empty or corrupted.")
        return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data for {band}: {e}")
        return pd.DataFrame(), pd.DataFrame()
    
# Load data for all bands
data_dict = {}
for band in bands:
    with st.spinner(f"Loading {band} data..."):
        notebook_data, ckplus_data = load_data(band)
        data_dict[band] = {"notebook": notebook_data, "ckplus": ckplus_data}

# Load last updated times for all bands
last_updated_dict = get_last_updated_times(bands)

# ---- NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=bands,
    icons=["music-note", "music-note", "music-note", "music-note"],  # Added icons for each band
    orientation="horizontal",
)

# CSS for centering tabs and styling tables
st.markdown("""
    <style>
    /* Center tab navigation */
    div[data-testid="stHorizontalBlock"] {
        display: flex;
        justify-content: center;
    }
    div[data-testid="stVerticalBlock"] > div.stTabs > div.stTabsSingleContent {
        align-items: center;
    }
    div.stTabs > div.stTabsSingleContent {
        align-items: center;
    }
    button[data-baseweb="tab"] {
        margin: 0 auto;
    }
    div[role="tablist"] {
        display: flex;
        justify-content: center;
    }
    
    /* Center table headers */
    .stTable th {
        text-align: center !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- TABS AND TABLES ---
if selected in bands:
    st.markdown(f"<h2 style='text-align: center;'>{band_names[selected]}</h2>", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs([f"{band_notebooks[selected]} Notebook", "CK+"])
    
    # Notebook tab
    with tab1:
        # Show next show info for Goose and WSP
        if selected in ["Goose", "WSP", "Phish"]:
            show_info = get_next_show_info(selected)
            if show_info:
                st.markdown(
                    f"<h4 style='text-align: center;'>Predictions for next show: {show_info.get('date', '?')} at {show_info.get('venue', '?')} in {show_info.get('city', '?')}, {show_info.get('state', '?')}</h4>",
                    unsafe_allow_html=True
                )
        st.markdown(f"<h3 style='text-align: center;'>{band_notebooks[selected]} Notebook Predictions</h3>", unsafe_allow_html=True)
        st.table(data_dict[selected]["notebook"])
        # Format last updated string
        last_raw = last_updated_dict.get(selected, 'Unknown')
        try:
            if last_raw != 'Unknown':
                dt = datetime.datetime.fromisoformat(last_raw)
                formatted = dt.strftime('%B %d, %Y %I:%M %p')
            else:
                formatted = 'Unknown'
        except Exception:
            formatted = last_raw
        st.caption(f"Predictions made with data last updated: {formatted}")
    
    # CK+ tab
    with tab2:
        # Show next show info for Goose and WSP
        if selected in ["Goose", "WSP", "Phish"]:
            show_info = get_next_show_info(selected)
            if show_info:
                st.markdown(
                    f"<h4 style='text-align: center;'>Predictions for next show: {show_info.get('date', '?')} at {show_info.get('venue', '?')} in {show_info.get('city', '?')}, {show_info.get('state', '?')}</h4>",
                    unsafe_allow_html=True
                )
        st.markdown("<h3 style='text-align: center;'>CK+ Predictions</h3>", unsafe_allow_html=True)
        st.table(data_dict[selected]["ckplus"])
        # Format last updated string
        last_raw = last_updated_dict.get(selected, 'Unknown')
        try:
            if last_raw != 'Unknown':
                dt = datetime.datetime.fromisoformat(last_raw)
                formatted = dt.strftime('%B %d, %Y %I:%M %p')
            else:
                formatted = 'Unknown'
        except Exception:
            formatted = last_raw
        st.caption(f"Predictions made with data last updated: {formatted}")

# Add a footer with additional information
st.markdown("---")
st.markdown(f"<h2 style='text-align: center;'>About Jam Band Nerd</h2>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center;'>This application provides insights and analysis for various jam bands' performances.</h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center;'>If you wish to contact administrators, please email jambandnerd@gmail.com.</h3>", unsafe_allow_html=True)