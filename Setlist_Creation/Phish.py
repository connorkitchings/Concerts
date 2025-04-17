from typing import Tuple, Optional
from SetlistCollector import SetlistCollector
from pathlib import Path
from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import logging

SONG_TABLE_IDX = 0


class PhishSetlistCollector(SetlistCollector):
    """Scraper for Phish show data using phish.net API."""

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize PhishSetlistCollector.
        
        Args:
            credentials_path: Path to credentials file. If None, looks in default location.
        """
        super().__init__(band='Phish')
        
        if credentials_path is None:
            current_dir = Path(__file__).resolve()
            three_dirs_up = current_dir.parent.parent.parent
            credentials_path = three_dirs_up / "Credentials" / "phish_net.txt"
            
        try:
            with open(credentials_path) as f:
                self.api_key = f.readline().strip().split(": ")[1].strip("'")
        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file not found at {credentials_path}")
        
        # Set today's date
        self.today = datetime.today().strftime('%Y-%m-%d')
        
    def _make_api_request(self, endpoint: str) -> dict:
        """
        Make request to phish.net API.
        
        Args:
            endpoint: API endpoint to query
            
        Returns:
            JSON response data
        """
        url = f"https://api.phish.net/v5/{endpoint}.json?apikey={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def load_song_data(self) -> pd.DataFrame:
        """Load and process song data from API and website."""
        # Get song list from API and scrape additional info from website
        song_data = pd.DataFrame(self._make_api_request('songs')['data'])
        song_data = song_data.drop(columns=['slug', 'last_permalink', 'debut_permalink'])

        response = requests.get("https://phish.net/song")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = pd.read_html(StringIO(str(soup.find_all('table'))))
        if not tables or len(tables) <= SONG_TABLE_IDX:
            logging.error(f"Expected table at index {SONG_TABLE_IDX} not found in Phish song page.")
            return pd.DataFrame()
        website_data = tables[SONG_TABLE_IDX].sort_values(by='Song Name').reset_index(drop=True)
        # Merge and clean up data
        merged_data = song_data.merge(
            website_data,
            left_on="song",
            right_on="Song Name",
            how="inner"
        )
        final_columns = {
            'songid': 'song_id',
            'Song Name': 'song',
            'Original Artist': 'original_artist',
            'Debut': 'debut_date'
        }
        return merged_data[list(final_columns.keys())].rename(columns=final_columns)
    
    def load_show_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and process show and venue data."""
        shows = pd.DataFrame(self._make_api_request('shows/artist/phish')['data'])

        # Split into past and future shows
        past_shows = shows[shows['showdate'] < self.today]
        future_shows = shows[shows['showdate'] >= self.today].sort_values('showdate').head(1)
        all_shows = pd.concat([past_shows, future_shows])

        # Create venue dataset
        venue_data = (
            all_shows[['venueid', 'venue', 'city', 'state', 'country']]
            .drop_duplicates()
            .sort_values('venueid')
            .reset_index(drop=True)
        )

        # Create show dataset
        show_data = (
            all_shows[['showid', 'showdate', 'venueid', 'tourid',
                       'exclude_from_stats', 'setlist_notes']]
            .sort_values('showdate')
            .reset_index(names='show_number')
            .assign(show_number=lambda x: x['show_number'] + 1)
        )

        show_data['tourid'] = show_data['tourid'].astype('Int64').astype(str)

        return show_data, venue_data

    def load_setlist_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and process setlist and transition data."""
        setlist_data = pd.DataFrame(self._make_api_request('setlists')['data'])

        # Create transition data
        transition_data = (setlist_data[['transition', 'trans_mark']]
                           .drop_duplicates()
                           .sort_values(by=['transition']))

        # Create setlist dataset
        setlist_columns = ['showid', 'uniqueid', 'songid', 'set', 'position',
                          'transition', 'isreprise', 'isjam', 'isjamchart',
                          'jamchart_description', 'tracktime', 'gap',
                          'is_original', 'soundcheck', 'footnote', 'exclude']
        
        return setlist_data[setlist_columns], transition_data

    def create_and_save_data(self) -> None:
        """Save Phish data to CSV files in the data directory."""
        
        logging.info("Loading Song Data")
        song_data = self.load_song_data()
        logging.info("Loading Show and Venue Data")
        show_data, venue_data = self.load_show_data()
        logging.info("Loading Setlist and Transition Data")
        setlist_data, transition_data = self.load_setlist_data()
    
        try:
            # Define files to save
            data_pairs = {
                'songdata.csv': song_data,
                'showdata.csv': show_data,
                'venuedata.csv': venue_data,
                'setlistdata.csv': setlist_data,
                'transitiondata.csv': transition_data
            }
            
            # Save each file
            logging.info("Saving data.")
            for filename, data in data_pairs.items():
                filepath = self.data_dir / filename
                data.to_csv(filepath, index=False)
        
        except Exception as e:
            logging.error(f"Error saving Phish data: {e}")