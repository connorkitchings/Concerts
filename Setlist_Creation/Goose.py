from typing import Tuple, Optional
from SetlistCollector import SetlistCollector
from pathlib import Path
from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import logging
import json
import os

SONG_TABLE_IDX = 1


class GooseSetlistCollector(SetlistCollector):
    """Scraper for Goose show data using phish.net API."""

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize GooseSetlistCollector.
        
        Args:
            credentials_path: Path to credentials file. If None, looks in default location.
        """
        super().__init__(band='Goose')
        
        # Set today's date
        self.today = datetime.today().strftime('%Y-%m-%d')
        
    def _make_api_request(self, endpoint: str, version: str="v2") -> dict:
        """
        Make request to El Goose API.
        
        Args:
            endpoint: API endpoint to query
            
        Returns:
            JSON response data
        """
        url_templates = {
            "v1": "https://elgoose.net/api/v1/{}.json?",
            "v2": "https://elgoose.net/api/v2/{}.json?",
        }
        url = url_templates.get(version, "").format(endpoint)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def load_song_data(self) -> pd.DataFrame:
        """Load and process song data from API and website."""
        # Get song list from API and scrape additional info from website
        songdata_api = pd.DataFrame(self._make_api_request('songs', 'v2')['data']).drop(columns=['slug','created_at','updated_at'])

        # Get additional song info from website
        response = requests.get("https://elgoose.net/song/")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = pd.read_html(StringIO(str(soup.find_all('table'))))
        if not tables or len(tables) <= SONG_TABLE_IDX:
            logging.error(f"Expected table at index {SONG_TABLE_IDX} not found in Goose song page.")
            return pd.DataFrame()
        songdata_scrape = tables[SONG_TABLE_IDX].sort_values(by='Song Name').reset_index(drop=True)

        # Merge and clean up song data from API and website
        merged_data = songdata_api.merge(
            songdata_scrape,
            left_on="name",
            right_on="Song Name",
            how="inner"
        )
        
        columns = ['id','Song Name', 'isoriginal','Original Artist', 'Debut Date','Last Played','Times Played Live', 'Avg Show Gap']
        merged_data = merged_data[columns].copy()

        final_columns = {
            'id': 'song_id',
            'Song Name': 'song',
            'isoriginal': 'is_original',
            'Original Artist': 'original_artist',
            'Debut Date': 'debut_date',
            'Last Played': 'last_played',
            'Times Played Live': 'times_played',
            'Avg Show Gap': 'avg_show_gap'
        }

        return merged_data[list(final_columns.keys())].rename(columns=final_columns)
    
    def load_show_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load and process show, venue, and tour data."""
        shows = pd.DataFrame(self._make_api_request('shows', 'v2')['data'])

        # Split into past and future shows
        past_shows = shows[shows['showdate'] < self.today]
        future_shows = shows[shows['showdate'] >= self.today].sort_values('showdate').head(1)
        all_shows = pd.concat([past_shows, future_shows])
        all_shows = all_shows[(all_shows['artist'] == 'Goose')].copy().reset_index(drop=True)

        # Create venue dataset
        venue_data = (
            all_shows[['venue_id', 'venuename', 'city', 'state', 'country', 'location']]
            .drop_duplicates()
            .sort_values('venue_id')
            .reset_index(drop=True)
            .rename(columns={'venue': 'venue_name'})
        )

        # Create tour dataset
        tour_data = (
            all_shows[['tour_id', 'tourname']]
            .drop_duplicates()
            .sort_values('tour_id')
            .reset_index(drop=True)
        )

        # Create show dataset
        show_data = (
            all_shows[['show_id', 'showdate', 'venue_id', 'tour_id', 'showorder']]
            .sort_values('showdate')
            .reset_index(names='show_number')
            .rename(columns={'showdate': 'show_date', 'showorder': 'show_order'})
            .assign(show_number=lambda x: x['show_number'] + 1)
        )
        show_data['tour_id'] = show_data['tour_id'].astype('Int64').astype(str)

        return show_data, venue_data, tour_data

    def load_setlist_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and process setlist and transition data."""
        setlist_df = pd.DataFrame(self._make_api_request('setlists', 'v1')['data'])
        self.update_last_updated()  # Update timestamp
        # Save last_updated to a json file in the data directory
        os.makedirs(self.data_dir, exist_ok=True)
        with open(os.path.join(self.data_dir, 'last_updated.json'), 'w') as f:
            json.dump({'last_updated': self.last_updated}, f)

        # Create transition data
        transition_data = (setlist_df[['transition_id', 'transition']]
                           .drop_duplicates()
                           .sort_values(by=['transition_id']))
        
        setlist_data = setlist_df[setlist_df['artist'] == "Goose"].copy().reset_index(drop=True)
        # Create setlist dataset
        setlist_columns = ['uniqueid', 'show_id', 'song_id','setnumber','position','tracktime',
                            'transition_id','isreprise','isjam','footnote','isjamchart',
                            'jamchart_notes','soundcheck','isverified','isrecommended']

        return setlist_data[setlist_columns], transition_data
    
    def create_and_save_data(self) -> None:
        """Save Goose data to CSV files in the data directory."""
        
        logging.info("Loading Song Data")
        song_data = self.load_song_data()
        logging.info("Loading Show and Venue Data")
        show_data, venue_data, tour_data = self.load_show_data()
        logging.info("Loading Setlist and Transition Data")
        setlist_data, transition_data = self.load_setlist_data()
    
        try:
            # Define files to save
            data_pairs = {
                'songdata.csv': song_data,
                'showdata.csv': show_data,
                'venuedata.csv': venue_data,
                'tourdata.csv': tour_data,
                'setlistdata.csv': setlist_data,
                'transitiondata.csv': transition_data
            }
            
            # Save each file
            logging.info("Saving data.")
            for filename, data in data_pairs.items():
                filepath = self.data_dir / filename
                data.to_csv(filepath, index=False)

            # --- Save next_show.json ---
            # Find the next show after today
            today_dt = pd.to_datetime(self.today)
            future_shows = show_data[pd.to_datetime(show_data['show_date']) > today_dt]
            if not future_shows.empty:
                next_show_row = future_shows.sort_values('show_date').iloc[0]
                venue_row = venue_data[venue_data['venue_id'] == next_show_row['venue_id']]
                if not venue_row.empty:
                    venue_info = venue_row.iloc[0]
                    next_show = {
                        "date": str(next_show_row['show_date']),
                        "venue_id": int(next_show_row['venue_id']),
                        "venue": venue_info['venuename'],
                        "city": venue_info['city'],
                        "state": venue_info['state']
                    }
                else:
                    next_show = {
                        "date": str(next_show_row['show_date']),
                        "venue_id": int(next_show_row['venue_id']),
                        "venue": None,
                        "city": None,
                        "state": None
                    }
            else:
                next_show = None
            # Write JSON to From Web directory
            from_web_dir = Path(self.data_dir) / "From Web"
            os.makedirs(from_web_dir, exist_ok=True)
            with open(from_web_dir / "next_show.json", "w") as f:
                json.dump({"next_show": next_show}, f, indent=2)

        except Exception as e:
            logging.error(f"Error saving Goose data: {e}")