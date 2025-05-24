import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import json
import numpy as np
from typing import Dict, Tuple, Optional, List

# --- Constants ---
DATA_DIR = Path("../3 - Data")
BANDS = {
    "WSP": {
        "name": "Widespread Panic",
        "predictions": ["notebook", "ck+"]
    },
    "Phish": {
        "name": "Phish",
        "predictions": ["notebook", "ck+"]
    },
    "Goose": {
        "name": "Goose",
        "predictions": ["notebook", "ck+"]
    },
    "UM": {
        "name": "Umphrey's McGee",
        "predictions": ["notebook", "ck+"]
    }
}

# --- Page Config ---
st.set_page_config(
    page_title="Jam Band Nerd",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading Functions ---
@st.cache_data
def load_show_data(band: str) -> pd.DataFrame:
    """Load and preprocess show data for a specific band."""
    try:
        # Try to load from the EverydayCompanion directory
        show_path = DATA_DIR / band / "EverydayCompanion" / "showdata.csv"
        if not show_path.exists():
            st.warning(f"Show data not found at {show_path}")
            return pd.DataFrame()
            
        df = pd.read_csv(show_path, parse_dates=['showdate'])
        
        # Add year and month columns if they don't exist
        if 'showdate' in df.columns and pd.api.types.is_datetime64_any_dtype(df['showdate']):
            df['year'] = df['showdate'].dt.year
            df['month'] = df['showdate'].dt.month
        
        df['band'] = band
        return df
    except Exception as e:
        st.error(f"Error loading {band} show data: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_song_data(band: str) -> pd.DataFrame:
    """Load and preprocess song performance data for a specific band."""
    try:
        # Try to load from the EverydayCompanion directory
        song_path = DATA_DIR / band / "EverydayCompanion" / "setlistdata.csv"
        if not song_path.exists():
            st.warning(f"Song data not found at {song_path}")
            return pd.DataFrame()
            
        df = pd.read_csv(song_path, parse_dates=['showdate'])
        df['band'] = band
        return df
    except Exception as e:
        st.error(f"Error loading {band} song data: {str(e)}")
        return pd.DataFrame()

def load_prediction(band: str, model_type: str) -> Tuple[pd.DataFrame, str]:
    """Load prediction data for a specific band and model type."""
    try:
        predictions_dir = DATA_DIR / band / "Predictions"
        prediction_file = None
        
        # Check for known file naming patterns
        possible_files = [
            f"today{model_type.lower()}.csv",  # todaynotebook.csv or todayck+.csv
            f"todays{model_type.lower()}.csv",  # todaysnotebook.csv or todaysck+.csv
            f"{model_type.lower()}.csv",        # notebook.csv or ck+.csv
        ]
        
        # Look for the first matching file
        for filename in possible_files:
            file_path = predictions_dir / filename
            if file_path.exists():
                prediction_file = file_path
                break
        
        # If no exact match, try pattern matching
        if not prediction_file or not prediction_file.exists():
            pattern = f"*{model_type.lower()}*.csv"
            files = list(predictions_dir.glob(pattern))
            if files:
                prediction_file = max(files, key=lambda x: x.stat().st_mtime)
        
        if not prediction_file or not prediction_file.exists():
            return pd.DataFrame(), f"No prediction file found for {band} - {model_type}"
        
        # Load the prediction file
        timestamp = datetime.fromtimestamp(prediction_file.stat().st_mtime)
        df = pd.read_csv(prediction_file)
        
        # Standardize column names
        column_map = {
            'Song': 'song',
            'Title': 'song',
            'Probability': 'probability',
            'Prediction': 'prediction',
            'Score': 'score'
        }
        df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
        
        # Add metadata
        df['band'] = band
        df['model_type'] = model_type
        
        return df, f"Last updated: {timestamp.strftime('%Y-%m-%d %H:%M')}"
        
    except Exception as e:
        st.error(f"Error loading {band} {model_type} predictions: {str(e)}")
        return pd.DataFrame(), f"Error loading predictions: {str(e)}"

# --- Visualization Functions ---
def plot_song_frequency(df: pd.DataFrame, song: str) -> go.Figure:
    """Plot frequency of a song over time."""
    song_df = df[df['song'] == song].copy()
    song_df = song_df.groupby('year').size().reset_index(name='count')
    
    fig = px.bar(
        song_df, 
        x='year', 
        y='count',
        title=f"{song} - Plays by Year",
        labels={'count': 'Number of Plays', 'year': 'Year'}
    )
    fig.update_layout(showlegend=False)
    return fig

def plot_venue_heatmap(df: pd.DataFrame) -> go.Figure:
    """Create a heatmap of shows by venue and year."""
    venue_year = df.groupby(['venue', 'year']).size().unstack(fill_value=0)
    
    fig = px.imshow(
        venue_year,
        labels=dict(x="Year", y="Venue", color="Shows"),
        title="Shows by Venue and Year"
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Venue",
        height=600
    )
    return fig

def plot_song_network(song_data: pd.DataFrame) -> go.Figure:
    """Create a network graph of song co-occurrence."""
    # This is a simplified example - you'd need to implement the co-occurrence logic
    # For now, returning an empty figure
    fig = go.Figure()
    fig.update_layout(
        title="Song Co-occurrence Network",
        showlegend=False,
        height=600
    )
    return fig

# --- Main App ---
def main():
    # Sidebar with band and model selection
    st.sidebar.title("Jam Band Nerd")
    
    # Band selection
    selected_band = st.sidebar.selectbox(
        "Select Band",
        list(BANDS.keys()),
        format_func=lambda x: BANDS[x]["name"]
    )
    
    # Model selection
    available_models = BANDS[selected_band]["predictions"]
    selected_models = st.sidebar.multiselect(
        "Select Prediction Models",
        available_models,
        default=available_models[:1]
    )
    
    # Load data for the selected band
    show_data = load_show_data(selected_band)
    song_data = load_song_data(selected_band)
    
    # Load predictions for selected models
    all_predictions = []
    model_updates = []
    
    for model in selected_models:
        pred_df, update_msg = load_prediction(selected_band, model)
        if not pred_df.empty:
            all_predictions.append(pred_df)
            model_updates.append(f"{model}: {update_msg}")
    
    predictions = pd.concat(all_predictions, ignore_index=True) if all_predictions else pd.DataFrame()
    
    # Year range filter
    if not show_data.empty:
        min_year = int(show_data['year'].min())
        max_year = int(show_data['year'].max())
        year_range = st.sidebar.slider(
            "Year Range",
            min_year, max_year, (max(1990, max_year-5), max_year)
        )
        
        # Filter data based on year range
        filtered_shows = show_data[
            (show_data['year'] >= year_range[0]) & 
            (show_data['year'] <= year_range[1])
        ].copy()
        
        # Main content
        st.title(f"{BANDS[selected_band]['name']} Show Analysis")
        
        # Show update status for each model
        if model_updates:
            st.markdown("**Prediction Data Status**")
            for update in model_updates:
                st.caption(update)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Shows", filtered_shows.shape[0])
        with col2:
            st.metric("Unique Venues", filtered_shows['venue'].nunique())
        with col3:
            st.metric("First Show", filtered_shows['showdate'].min().strftime('%Y-%m-%d'))
        with col4:
            st.metric("Last Show", filtered_shows['showdate'].max().strftime('%Y-%m-%d'))
        
        # Tabs for different visualizations
        tab1, tab2, tab3 = st.tabs([
            "Predictions", 
            "Song Analysis", 
            "Venue Analysis"
        ])
        
        with tab1:
            st.header("Song Predictions")
            if not predictions.empty:
                # Group by model type if multiple models selected
                if len(selected_models) > 1:
                    for model in selected_models:
                        model_df = predictions[predictions['model_type'] == model]
                        if not model_df.empty:
                            st.subheader(f"{model} Predictions")
                            st.dataframe(
                                model_df.style.background_gradient(
                                    cmap='YlOrRd', 
                                    subset=[col for col in model_df.columns if 'prob' in col.lower()]
                                ),
                                use_container_width=True,
                                hide_index=True
                            )
                            st.markdown("---")
                else:
                    st.dataframe(
                        predictions.style.background_gradient(
                            cmap='YlOrRd',
                            subset=[col for col in predictions.columns if 'prob' in col.lower()]
                        ),
                        use_container_width=True,
                        hide_index=True
                    )
            else:
                st.warning("No prediction data available for the selected models")
        
        with tab2:
            st.header("Song Analysis")
            if not song_data.empty:
                song_list = sorted(song_data['song'].unique())
                selected_song = st.selectbox("Select a song", song_list, key="song_selector")
                fig = plot_song_frequency(song_data, selected_song)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No song data available")
        
        with tab3:
            st.header("Venue Analysis")
            if not filtered_shows.empty:
                fig = plot_venue_heatmap(filtered_shows)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No venue data available")
    
    else:
        st.error(f"Failed to load show data for {BANDS[selected_band]['name']}. Please check the data files.")

if __name__ == "__main__":
    main()
