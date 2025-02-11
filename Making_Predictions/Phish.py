from PredictionMaker import PredictionMaker
from datetime import date, timedelta
from typing import Tuple, Dict, Optional
import pandas as pd
from pathlib import Path

class PhishPredictionMaker(PredictionMaker):
    """Predictor for Phish setlists."""

    def __init__(self):
        """
        Initialize PhishPredictionMaker.
        """
        super().__init__(band='Phish')
        # Remove duplicate declarations
        self.song_filename = "songdata.csv"
        self.venue_filename = "venuedata.csv"
        self.show_filename = "showdata.csv"
        
        # Convert data_dir and pred_dir to Path object if not already
        self.data_dir = Path(self.data_dir)
        self.pred_dir = Path(self.pred_dir)
        
        # Set today's date as date object
        self.today = date.today()
        
        # Initialize DataFrame attributes
        self.songdata = None
        self.venuedata = None
        self.showdata = None
        self.transitiondata = None
        self.setlistdata = None
        self.setlist_by_song = None
        self.last_show = None
        
    def load_data(self) -> Tuple[pd.DataFrame, ...]:
        """Load band data from data directory"""
        
        files = ["songdata.csv", "venuedata.csv", "showdata.csv", "transitiondata.csv", "setlistdata.csv"]
        data = {file.split('.')[0]: pd.read_csv(self.data_dir / file) for file in files}

        # Access individual DataFrames
        self.songdata = data["songdata"]
        self.venuedata = data["venuedata"]
        self.showdata = data["showdata"]
        self.showdata = self.showdata[self.showdata['exclude_from_stats'] != 1].copy().reset_index(drop=True)
        self.transitiondata = data["transitiondata"]  # Fixed typo
        self.setlistdata = data["setlistdata"]
        
        self.last_show = self.showdata['show_number'].max() - 1
        
        return tuple(data.values())
    
    def get_setlist_by_song(self) -> pd.DataFrame:
        """Create setlist_by_song dataframe from loaded data"""
        if any(df is None for df in [self.setlistdata, self.showdata]):
            raise ValueError("Data must be loaded first using load_data()")
            
        setlist_by_song = pd.merge(self.setlistdata,
                                   self.showdata,
                                   on='showid', 
                                   how='left').sort_values(['songid','show_number']).reset_index(drop=True)
        
        setlist_by_song['gap'] = setlist_by_song.groupby('songid')['show_number'].diff()
        setlist_by_song.loc[setlist_by_song.groupby('songid').head(1).index, 'gap'] = None     
        
        self.setlist_by_song = setlist_by_song
        return setlist_by_song
    
    def create_ckplus(self) -> pd.DataFrame: 
        """Create CK+ prediction dataset"""
        if self.setlist_by_song is None:
            raise ValueError("Must run get_setlist_by_song() first")
        
        my_song_data = (self.setlist_by_song[self.setlist_by_song['isreprise'] == 0]
                .merge(self.songdata[['song_id', 'song', 'original_artist']], 
                       left_on='songid', 
                       right_on='song_id', 
                       how='left').drop(columns=['song_id'])
                .groupby(['song', 'is_original'])
                .agg({
                    'show_number': ['count', 'min', 'max'],
                    'gap': ['min', 'max', 'mean', 'median', 'std']
                })
                .reset_index()
                .round(2)
               )

        my_song_data.columns = ['_'.join(col).strip() for col in my_song_data.columns.values]

        # Rename columns for easier access
        my_song_data = my_song_data.rename(columns={
            'song_': 'song', 
            'is_original_': 'is_original',
            'show_number_count': 'times_played_total', 
            'show_number_min': 'debut', 
            'show_number_max': 'last_played', 
            'gap_min': 'min_gap', 
            'gap_max': 'max_gap', 
            'gap_mean': 'avg_gap',
            'gap_median': 'med_gap',  
            'gap_std': 'std_gap'
        })

        my_song_data['is_original'] = my_song_data['is_original'].astype(int)
        my_song_data['current_gap'] = self.last_show - my_song_data['last_played']
        
        my_song_data = (
            my_song_data
            .merge(
                self.showdata[['show_number', 'showdate']], 
                left_on='debut', 
                right_on='show_number', 
                how='left'
            )
            .rename(columns={'showdate': 'debut_date'})
            .drop(columns=['show_number', 'debut'])
            .merge(
                self.showdata[['show_number', 'showdate']], 
                left_on='last_played', 
                right_on='show_number', 
                how='left'
            )
            .rename(columns={'showdate': 'ltp_date'})
            .drop(columns=['show_number', 'last_played'])
        )[['song', 'is_original', 'times_played_total','debut_date','ltp_date','current_gap','avg_gap', 'med_gap', 'std_gap']]
        
        my_song_data['gap_zscore'] = (my_song_data['current_gap'] - my_song_data['avg_gap']) / my_song_data['std_gap']
        
        five_years_ago = pd.Timestamp(date.today() - timedelta(days=5*365))
        my_song_data['ltp_date'] = pd.to_datetime(my_song_data['ltp_date'], format='%Y-%m-%d').dt.date

        ck_plus = (my_song_data[(my_song_data['is_original'] == 1) & 
                                (my_song_data['times_played_total'] > 10)
                                &(my_song_data['ltp_date'] > five_years_ago)].copy()           
           .sort_values(by='gap_zscore', ascending=False)
           .reset_index(drop=True)
           .drop(columns=['is_original','debut_date', 'std_gap','gap_zscore'])
)
        
        ck_plus['current_minus_avg'] = ck_plus['current_gap'] - ck_plus['avg_gap']
        ck_plus['current_minus_med'] = ck_plus['current_gap'] - ck_plus['med_gap']
        
        return ck_plus
    
    def create_notebook(self) -> pd.DataFrame: 
        """Create Rick's Notebook prediction dataset"""
        if self.setlist_by_song is None:
            raise ValueError("Must run get_setlist_by_song() first")
            
        one_year_ago = (self.today - timedelta(days=366)).strftime('%Y-%m-%d')
        
        treys_notebook_data = (
            self.setlist_by_song[
                (self.setlist_by_song['isreprise'] == 0) & 
                (self.setlist_by_song['showdate'] > one_year_ago)
            ]
            .merge(
                self.songdata[['song_id', 'song']], 
                left_on='songid', 
                right_on='song_id',  
                how='left'
            )
            .drop(columns=['song_id'])
        )[['song', 'is_original', 'show_number', 'showdate', 'gap']]

        treys_notebook = (
            treys_notebook_data
            .groupby(['song', 'is_original'])
            .agg({
                'show_number': ['count', 'max'],
                'gap': ['min', 'max', 'mean', 'median', 'std']
            })
            .reset_index()
            .round(2)
        )
        treys_notebook.columns = ['_'.join(col).strip() for col in treys_notebook.columns.values]

        treys_notebook = treys_notebook.rename(columns={
            'song_': 'song', 
            'is_original_': 'is_original',
            'show_number_count': 'times_played_in_last_year', 
            'show_number_max': 'last_played', 
            'gap_min': 'min_gap', 
            'gap_max': 'max_gap', 
            'gap_mean': 'avg_gap',
            'gap_median': 'med_gap',  
            'gap_std': 'std_gap'
        })

        treys_notebook['is_original'] = treys_notebook['is_original'].astype(int)
        treys_notebook['current_gap'] = self.last_show - treys_notebook['last_played']

        treys_notebook = (
            treys_notebook
            .merge(
                self.showdata[['show_number', 'showdate']], 
                left_on='last_played', 
                right_on='show_number', 
                how='left'
            )
            .rename(columns={'showdate': 'ltp_date'})
            .drop(columns=['show_number', 'last_played'])
        )[['song', 'is_original', 'times_played_in_last_year', 'ltp_date',
           'current_gap', 'avg_gap', 'med_gap']]

        treys_notebook = (
            treys_notebook[
                (treys_notebook['is_original'] == 1) & 
                (treys_notebook['current_gap'] > 3)
            ]
            .sort_values(by='times_played_in_last_year', ascending=False)
            .reset_index(drop=True)
            .drop(columns=['is_original'])
        )
                        
        return treys_notebook
        
    def create_and_save_predictions(self):
        """Create and save prediction datasets"""
        self.load_data()
        self.get_setlist_by_song()
        
        ck_plus = self.create_ckplus()
        treys_notebook = self.create_notebook()
        
        try:
            # Create predictions directory if it doesn't exist
            predictions_dir = self.pred_dir
            
            # Define files to save
            data_pairs = {
                'ck_plus.csv': ck_plus,
                'treys_notebook.csv': treys_notebook
            }
            
            # Save each file
            print("Saving prediction data...")
            for filename, data in data_pairs.items():
                filepath = predictions_dir / filename
                data.to_csv(filepath, index=False)
                print(f"Saved {filename}")
                
        except Exception as e:
            print(f"Error saving prediction data: {e}")