import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from logger import get_logger

logger = get_logger(__name__)

def load_setlist_and_showdata(setlist_path, venuedata_path, songdata_path):
    """
    Loads setlist data for UM, standardizes columns for modeling.
    Returns DataFrame with 'song', 'show_date', and 'venue' columns.
    """
    df = pd.read_csv(setlist_path)
    # Standardize columns
    df = df.rename(columns={
        'Date Played': 'show_date',
        'Song Name': 'song',
        'Venue': 'venue'
    })
    df['show_date'] = pd.to_datetime(df['show_date'], errors='coerce')
    df = df[~df['song'].isnull()].copy()
    # Optionally, merge venue info if needed:
    # venue_df = pd.read_csv(venuedata_path)
    # df = df.merge(venue_df, left_on='venue', right_on='Venue Name', how='left')
    logger.info(f"Loaded setlist ({len(df):,}) rows from {setlist_path}, venues from {venuedata_path}, songs from {songdata_path}")
    return df
