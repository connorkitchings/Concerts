import pandas as pd
from pathlib import Path
from logger import get_logger
from UM.config import DATA_DIR

logger = get_logger(__name__, add_console_handler=True)

SHOW_DATA_FILENAME = 'showdata.csv'

def create_show_data(setlist_data: pd.DataFrame, data_dir: str | Path = None) -> pd.DataFrame:
    """
    Create a DataFrame for showdata.csv: one row per show with unique show ID/link, date, venue, city, state, country, and sequential show_number.

    Args:
        setlist_data (pd.DataFrame): DataFrame containing setlist data with show-level columns.
        data_dir (str | Path, optional): Directory to save showdata.csv. Defaults to DATA_DIR.

    Returns:
        pd.DataFrame: DataFrame of unique shows with sequential show_number.
    """
    data_dir = Path(data_dir) if data_dir is not None else Path(DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    if setlist_data.empty:
        logger.warning("No setlist data provided to create_show_data.")
        return pd.DataFrame()
    # Extract unique shows based on link (show_id), date, venue, city, state, country
    show_cols = ['link', 'date', 'venue', 'city', 'state', 'country']
    shows = setlist_data[show_cols].drop_duplicates().copy()
    # Parse date for sorting
    shows['parsed_date'] = pd.to_datetime(shows['date'], errors='coerce')
    shows = shows.sort_values('parsed_date').reset_index(drop=True)
    shows['show_number'] = shows.index + 1
    shows = shows.drop(columns=['parsed_date'])
    # Save to CSV
    showdata_path = data_dir / SHOW_DATA_FILENAME
    shows.to_csv(showdata_path, index=False)
    from UM.utils import print_relative_path
    logger.info(f"Saved showdata.csv with {len(shows)} shows to ", end='')
    print_relative_path(showdata_path)
    return shows
