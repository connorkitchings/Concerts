from PredictionMaker import PredictionMaker
from datetime import date, timedelta
from typing import Tuple, Dict, Optional
import pandas as pd
from pathlib import Path

class UMPredictionMaker(PredictionMaker):
    """Predictor for Umphrey's McGee (UM) setlists."""

    def __init__(self):
        """
        Initialize UMPredictionMaker.
        """
        super().__init__(band='UM')
        # Convert data_dir and pred_dir to Path object if not already
        self.data_dir = Path(self.data_dir)
        self.pred_dir = Path(self.pred_dir)
        
        # Set today's date as date object
        self.today = date.today()
        
        # Initialize DataFrame attributes
        self.songdata = None
        self.venuedata = None
        self.setlistdata = None
        self.setlist_by_song = None
        self.last_show = None
        
    def load_data(self) -> Tuple[pd.DataFrame, ...]:
        """Load band data from data directory"""
        
        files = ["songdata.csv", "venuedata.csv", "setlistdata.csv"]
        data = {file.split('.')[0]: pd.read_csv(self.data_dir / file) for file in files}

        # Access individual DataFrames
        self.songdata = data["songdata"]
        self.songdata['Song Name'] = self.songdata['Song Name'].str.strip()
        
        self.venuedata = data["venuedata"]
        
        self.setlistdata = data["setlistdata"].dropna(subset='Song Name').reset_index(drop=True)
        self.setlistdata['Song Name'] = self.setlistdata['Song Name'].str.strip()
        
        # Convert Date Played to datetime
        self.setlistdata['Date Played'] = pd.to_datetime(self.setlistdata['Date Played'])
        
        # Sort by date and song name
        self.setlistdata = self.setlistdata.sort_values(by=['Date Played', 'Song Name']).reset_index(drop=True)
        
        # Calculate the isreprise column (whether a song appears multiple times in the same show)
        self.setlistdata['isreprise'] = self.setlistdata.groupby(['Date Played', 'Song Name']).cumcount().astype(int)
        
        # Remove reprises to only keep the first occurrence of each song in a show
        self.setlistdata = self.setlistdata[self.setlistdata['isreprise']==0].copy().reset_index(drop=True)
        
        # Create a show_index column to track show order
        self.setlistdata['show_index'] = self.setlistdata['Date Played'].rank(method='dense').astype(int)
        
        # Get the last show index
        self.last_show = self.setlistdata['show_index'].max()
        
        return tuple(data.values())
    
    def get_setlist_by_song(self) -> pd.DataFrame:
        """Create setlist_by_song dataframe from loaded data"""
        if self.setlistdata is None:
            raise ValueError("Data must be loaded first using load_data()")
            
        # Group by Song Name and Date Played
        setlist_by_song = self.setlistdata.copy()
        
        # Sort by song name and date
        setlist_by_song = setlist_by_song.sort_values(['Song Name', 'Date Played']).reset_index(drop=True)
        
        # Calculate gap between performances for each song
        setlist_by_song['gap'] = setlist_by_song.groupby('Song Name')['show_index'].diff()
        
        # Set gap to None for first appearance of each song
        setlist_by_song.loc[setlist_by_song.groupby('Song Name').head(1).index, 'gap'] = None 
        
        self.setlist_by_song = setlist_by_song.copy()
        
        return setlist_by_song
    
    def create_ckplus(self) -> pd.DataFrame: 
        """Create CK+ prediction dataset (songs overdue to be played)"""
        if self.setlist_by_song is None:
            raise ValueError("Must run get_setlist_by_song() first")
        
        # Aggregate statistics for each song
        my_song_data = (self.setlist_by_song.groupby(['Song Name'])
                        .agg({
                            'show_index': ['count', 'min', 'max'],
                            'gap': ['min', 'max', 'mean', 'median', 'std']
                            })
                        .reset_index()
                        .round(2)
                        )
        
        # Flatten multi-level column names
        my_song_data.columns = ['_'.join(col).strip() for col in my_song_data.columns.values]

        # Rename columns for easier access
        my_song_data = my_song_data.rename(columns={
            'Song Name_': 'song_name', 
            'show_index_count': 'times_played_total', 
            'show_index_min': 'debut', 
            'show_index_max': 'last_played', 
            'gap_min': 'min_gap', 
            'gap_max': 'max_gap', 
            'gap_mean': 'avg_gap',
            'gap_median': 'med_gap',  
            'gap_std': 'std_gap'
            })
        
        # Calculate current gap (shows since last played)
        my_song_data['current_gap'] = self.last_show - my_song_data['last_played']
        
        # Get debut and last played dates
        debut_dates = (self.setlist_by_song
                       .sort_values('Date Played')
                       .groupby('Song Name')
                       .first()
                       .reset_index()[['Song Name', 'Date Played']]
                       .rename(columns={'Date Played': 'debut_date'}))
        
        last_played_dates = (self.setlist_by_song
                            .sort_values('Date Played', ascending=False)
                            .groupby('Song Name')
                            .first()
                            .reset_index()[['Song Name', 'Date Played']]
                            .rename(columns={'Date Played': 'ltp_date'}))
        
        # Merge date information
        my_song_data = (my_song_data
                       .merge(debut_dates, left_on='song_name', right_on='Song Name', how='left')
                       .drop(columns=['Song Name'])
                       .merge(last_played_dates, left_on='song_name', right_on='Song Name', how='left')
                       .drop(columns=['Song Name', 'debut', 'last_played']))
        
        # Calculate gap z-score
        my_song_data['gap_zscore'] = (my_song_data['current_gap'] - my_song_data['avg_gap']) / my_song_data['std_gap']
        
        # Define cutoff date for "active" songs (last 5 years)
        five_years_ago = date.today() - timedelta(days=5*365)
        
        # Filter for songs played more than 10 times and played in the last 5 years
        ck_plus = (my_song_data[(my_song_data['times_played_total'] > 10) & 
                                (my_song_data['ltp_date'] > pd.Timestamp(five_years_ago))].copy()           
                   .sort_values(by='gap_zscore', ascending=False)
                   .reset_index(drop=True)
                   .drop(columns=['std_gap', 'gap_zscore'])
                   )
        
        # Calculate how much current gap exceeds average and median
        ck_plus['current_minus_avg'] = ck_plus['current_gap'] - ck_plus['avg_gap']
        ck_plus['current_minus_med'] = ck_plus['current_gap'] - ck_plus['med_gap']
        
        # Format dates for better readability
        ck_plus['debut_date'] = ck_plus['debut_date'].dt.strftime('%Y-%m-%d')
        ck_plus['ltp_date'] = ck_plus['ltp_date'].dt.strftime('%Y-%m-%d')
        
        return ck_plus
    
    def create_notebook(self) -> pd.DataFrame: 
        """Create Notebook prediction dataset (frequently played songs in recent period)"""
        if self.setlist_by_song is None:
            raise ValueError("Must run get_setlist_by_song() first")
            
        # Filter for shows in the last 2 years
        two_years_ago = date.today() - timedelta(days=2*366)
        recent_shows = self.setlist_by_song[self.setlist_by_song['Date Played'] > pd.Timestamp(two_years_ago)].copy()

        # Calculate statistics for songs played in recent period
        notebook = (
            recent_shows
            .groupby(['Song Name'])
            .agg({
                'show_index': ['count', 'max'],
                'gap': ['min', 'max', 'mean', 'median', 'std']
            })
            .reset_index()
            .round(2)
        )
        
        # Flatten multi-level column names
        notebook.columns = ['_'.join(col).strip() for col in notebook.columns.values]

        # Rename columns
        notebook = notebook.rename(columns={
            'Song Name_': 'song', 
            'show_index_count': 'times_played_in_last_2_years', 
            'show_index_max': 'last_played', 
            'gap_min': 'min_gap', 
            'gap_max': 'max_gap', 
            'gap_mean': 'avg_gap',
            'gap_median': 'med_gap',  
            'gap_std': 'std_gap'
        })
        
        # Calculate current gap
        notebook['current_gap'] = self.last_show - notebook['last_played']

        # Get last played date
        last_played_dates = (recent_shows
                            .sort_values('Date Played', ascending=False)
                            .groupby('Song Name')
                            .first()
                            .reset_index()[['Song Name', 'Date Played']]
                            .rename(columns={'Date Played': 'ltp_date'}))
        
        # Merge with date information
        notebook = notebook.merge(
            last_played_dates, 
            left_on='song', 
            right_on='Song Name', 
            how='left'
        ).drop(columns=['Song Name'])
        
        # Keep only relevant columns
        notebook = notebook[['song', 'times_played_in_last_2_years', 'ltp_date', 'current_gap', 'avg_gap', 'med_gap']]

        # Filter for songs with a gap > 3 shows
        notebook = (
            notebook[(notebook['current_gap'] > 3)]
            .sort_values(by='times_played_in_last_2_years', ascending=False)
            .reset_index(drop=True)
        )
        
        # Format date for better readability
        notebook['ltp_date'] = notebook['ltp_date'].dt.strftime('%Y-%m-%d')
                        
        return notebook
    
    def create_and_save_predictions(self):
        """Create and save prediction datasets"""
        self.load_data()
        self.get_setlist_by_song()
        
        ck_plus = self.create_ckplus()
        notebook = self.create_notebook()
        
        try:
            # Create predictions directory if it doesn't exist
            predictions_dir = self.pred_dir
            predictions_dir.mkdir(parents=True, exist_ok=True)
            
            # Define files to save
            data_pairs = {
                'ck_plus.csv': ck_plus,
                'notebook.csv': notebook
            }
            
            # Save each file
            for filename, data in data_pairs.items():
                filepath = predictions_dir / filename
                data.to_csv(filepath, index=False)
            
        except Exception as e:
            print(f"Error saving prediction data: {e}")