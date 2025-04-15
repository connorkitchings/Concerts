import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_option_menu import option_menu
from PIL import Image

# Define base directory and bands
base_dir = "/Users/connorkitchings/Desktop/Repositories/Concerts/"  # Replace with your actual base directory
bands = ["Goose", "Phish", "UM", "WSP"]
band_names = {"Goose": "Goose", "Phish": "Phish", "UM": "Umphrey's McGee", "WSP": "Widespread Panic"}
band_notebooks = {"Goose": "Rick's", "Phish": "Trey's", "UM": "Joel's", "WSP": "JoJo's"}

# --- CONFIGS ---
st.set_page_config(
    page_title="Jam Band Nerd Demo",
    page_icon="🎸",  # Added a guitar emoji as page icon
    layout="wide"
)

#st.title("Jam Band Nerd")
st.markdown("<h1 style='text-align: center;'>Jam Band Nerd</h1>", unsafe_allow_html=True)
#st.image("https://hevria.com/wp-content/uploads/2015/07/GD-rainbow2-1024x770.jpg")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://hevria.com/wp-content/uploads/2015/07/GD-rainbow2-1024x770.jpg")

# --- LOAD DATA ---
@st.cache_data
def load_data(band):
    """Load the notebook and CK+ data for a specific band"""
    try:
        data_notebook = pd.read_csv(Path(base_dir) / "Data" / band / "Predictions" / "notebook.csv")
        data_notebook.columns = ["Song", "Times Played in Last Year", "Last Time Played", "Current Gap", "Average Gap", "Median Gap"]
        data_notebook['Average Gap'] = data_notebook['Average Gap'].round(2)
        data_notebook['Median Gap'] = data_notebook['Median Gap'].round(2)
        data_ckplus = pd.read_csv(Path(base_dir) / "Data" / band / "Predictions" / "ck_plus.csv")
        data_ckplus.columns = ['Song', 'Times Played', 'Last Time Played', 'Current Gap', 'Average Gap', 'Median Gap', 'Current Minus Average', 'Current Minus Median']
        return data_notebook.head(50), data_ckplus.head(50)
    except Exception as e:
        st.error(f"Error loading data for {band}: {e}")
        # Return empty DataFrames if files don't exist
        return pd.DataFrame(), pd.DataFrame()
    
# Load data for all bands
data_dict = {}
for band in bands:
    notebook_data, ckplus_data = load_data(band)
    data_dict[band] = {"notebook": notebook_data, "ckplus": ckplus_data}

# ---- NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=bands,
    icons=["music-note", "music-note", "music-note", "music-note"],  # Added icons for each band
    orientation="horizontal",
)

st.markdown("""
    <style>
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
    </style>
""", unsafe_allow_html=True)

# --- TABS AND TABLES ---
if selected in bands:
    st.markdown(f"<h2 style='text-align: center;'>{band_names[selected]}</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs([f"{band_notebooks[selected]} Notebook","CK+"])
    with tab1:
        st.markdown(f"<h3 style='text-align: center;'>{band_notebooks[selected]} Notebook Predictions</h3>", unsafe_allow_html=True)
        #st.dataframe(data_dict[selected]["notebook"], height=1785)
        st.markdown("""
                    <style>
                    .stTable th {
                        text-align: center !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
        st.table(data_dict[selected]["notebook"])
    with tab2:
        st.markdown("<h3 style='text-align: center;'>CK+ Predictions</h3>", unsafe_allow_html=True)
        #st.dataframe(data_dict[selected]["ckplus"], height=1785)
        st.markdown("""
                    <style>
                    .stTable th {
                        text-align: center !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
        st.table(data_dict[selected]["ckplus"])

# Add a footer with additional information
st.markdown("---")
st.markdown(f"<h2 style='text-align: center;'>About Jam Band Nerd</h2>", unsafe_allow_html=True)
#st.markdown("### About Jam Band Nerd")
st.markdown(f"<h3 style='text-align: center;'>This application provides predictions for songs to be played at certain jam bands' next performances</h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center;'>If you wish to contact administrators, please email jambandnerd@gmail.com</h3>", unsafe_allow_html=True)
