import os
import pandas as pd
from logger import get_logger

logger = get_logger(__name__)

def load_setlist_and_showdata(
    setlist_path: str, venuedata_path: str, songdata_path: str
) -> pd.DataFrame:
    """
    Loads setlist data for UM, standardizes columns for modeling.

    Args:
        setlist_path (str): Path to setlistdata.csv
        venuedata_path (str): Path to venuedata.csv (not used in basic loader)
        songdata_path (str): Path to songdata.csv (not used in basic loader)

    Returns:
        pd.DataFrame: DataFrame with 'song', 'show_date', and 'venue' columns.
    """
    df = pd.read_csv(setlist_path)
    # Rename to modeling standard columns
    df = df.rename(columns={
        'date': 'show_date',
        # 'song' is already correct
        # 'venue' is already correct
    })
    df['show_date'] = pd.to_datetime(df['show_date'], errors='coerce')
    df = df[~df['song'].isnull()].copy()
    logger.info(f"Loaded setlist ({len(df):,}) rows from {setlist_path}, venues from {venuedata_path}, songs from {songdata_path}")
    return df
