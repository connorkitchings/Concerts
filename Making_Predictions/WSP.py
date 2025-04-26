from PredictionMaker import PredictionMaker
from datetime import date, timedelta
from typing import Tuple, Dict, Optional
import pandas as pd
from pathlib import Path

class WSPPredictionMaker(PredictionMaker):
    """Predictor for WSP setlists."""

    def __init__(self):
        """
        Initialize WSPPredictionMaker.
        """
        super().__init__(band='WSP')
        # Remove duplicate declarations
        self.song_filename = "songdata.csv"
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
        
        # Load all available collector output files for WSP
        files = ["songdata.csv", "venuedata.csv", "showdata.csv", "setlistdata.csv", "transitiondata.csv"]
        data = {}
        for file in files:
            path = self.data_dir / file
            if path.exists():
                data[file.split('.')[0]] = pd.read_csv(path)
            else:
                data[file.split('.')[0]] = None

        # Assign DataFrames using collector schema
        self.songdata = data["songdata"]
        if self.songdata is not None and 'song' in self.songdata.columns:
            self.songdata['song'] = self.songdata['song'].str.title()
        self.venuedata = data["venuedata"]
        self.showdata = data["showdata"]
        self.setlistdata = data["setlistdata"]
        if self.setlistdata is not None and 'song_name' in self.setlistdata.columns:
            self.setlistdata = self.setlistdata.dropna(subset=['song_name']).reset_index(drop=True)
            self.setlistdata['song_name'] = self.setlistdata['song_name'].str.title()
            # Efficiently remove reprises using collector's columns
            self.setlistdata = self.setlistdata.sort_values(by=['link', 'song_name', 'song_index_show']).reset_index(drop=True)
            self.setlistdata['isreprise'] = self.setlistdata.groupby(['link', 'song_name']).cumcount().astype(int)
            self.setlistdata = self.setlistdata[self.setlistdata['isreprise']==0].copy().sort_values(by=['link', 'song_index_show']).reset_index(drop=True)
        self.transitiondata = data["transitiondata"]

        # Use collector's show_number if available, else fallback
        if self.showdata is not None:
            if 'show_number' in self.showdata.columns:
                self.last_show = self.showdata['show_number'].max()
            elif 'show_index_overall' in self.showdata.columns:
                self.last_show = self.showdata['show_index_overall'].max()
            else:
                self.last_show = None
        else:
            self.last_show = None

        return tuple(data.values())
    
    def get_setlist_by_song(self) -> pd.DataFrame:
        """Create setlist_by_song dataframe from loaded data"""
        if any(df is None for df in [self.setlistdata, self.showdata]):
            raise ValueError("Data must be loaded first using load_data()")
            
        setlist_by_song = (pd.merge(self.setlistdata, 
                                    self.showdata, 
                                    on='link', 
                                    how='left')
                           .sort_values(['song_name','show_index_overall'])
                           .reset_index(drop=True))
        
        setlist_by_song = setlist_by_song[setlist_by_song['song_name']!='Jam'].copy().reset_index(drop=True)
        setlist_by_song['gap'] = setlist_by_song.groupby('song_name')['show_index_overall'].diff()
        setlist_by_song.loc[setlist_by_song.groupby('song_name').head(1).index, 'gap'] = None 
        
        self.setlist_by_song = setlist_by_song.copy()
        
        return setlist_by_song
    
    def create_ckplus(self) -> pd.DataFrame: 
        """Create CK+ prediction dataset"""
        if self.setlist_by_song is None:
            raise ValueError("Must run get_setlist_by_song() first")
        
        my_song_data = (self.setlist_by_song.groupby(['song_name'])
                        .agg({
                            'show_index_overall': ['count', 'min', 'max'],
                            'gap': ['min', 'max', 'mean', 'median', 'std']
                            })
                        .reset_index()
                        .round(2)
                        )
        
        my_song_data.columns = ['_'.join(col).strip() for col in my_song_data.columns.values]

        # Rename columns for easier access
        my_song_data = my_song_data.rename(columns={
            'song_name_': 'song_name', 
            'show_index_overall_count': 'times_played_total', 
            'show_index_overall_min': 'debut', 
            'show_index_overall_max': 'last_played', 
            'gap_min': 'min_gap', 
            'gap_max': 'max_gap', 
            'gap_mean': 'avg_gap',
            'gap_median': 'med_gap',  
            'gap_std': 'std_gap'
            })
        
        my_song_data['current_gap'] = self.last_show - my_song_data['last_played']
        
        my_song_data = (my_song_data
                        .merge(self.showdata[['show_index_overall', 'date']], left_on='debut', right_on='show_index_overall', how='left')
                        .rename(columns={'date': 'debut_date'}).drop(columns=['show_index_overall', 'debut'])
                        .merge(self.showdata[['show_index_overall', 'date']], left_on='last_played', right_on='show_index_overall', how='left')
                        .rename(columns={'date': 'ltp_date'}).drop(columns=['show_index_overall', 'last_played'])
                        )[['song_name', 'times_played_total','debut_date','ltp_date','current_gap','avg_gap', 'med_gap', 'std_gap']]
        
        my_song_data['gap_zscore'] = (my_song_data['current_gap'] - my_song_data['avg_gap']) / my_song_data['std_gap']
        
        five_years_ago = date.today() - timedelta(days=5*365)
        my_song_data['ltp_date'] = pd.to_datetime(my_song_data['ltp_date'], format='%m/%d/%y').dt.date

        ck_plus = (my_song_data[(my_song_data['times_played_total'] > 10) & 
                                (my_song_data['ltp_date'] > five_years_ago) &
                                (my_song_data['song_name'] != 'Drums')].copy()           
                   .sort_values(by='gap_zscore', ascending=False)
                   .reset_index(drop=True)
                   .drop(columns=['debut_date', 'std_gap','gap_zscore'])
                   )
        
        ck_plus['current_minus_avg'] = ck_plus['current_gap'] - ck_plus['avg_gap']
        ck_plus['current_minus_med'] = ck_plus['current_gap'] - ck_plus['med_gap']
        
        return ck_plus
    
    def create_notebook(self) -> pd.DataFrame: 
        """Create Notebook prediction dataset"""
        if self.setlist_by_song is None:
            raise ValueError("Must run get_setlist_by_song() first")
            
        one_year_ago = date.today() - timedelta(days=2*366)
        self.setlist_by_song['date'] = pd.to_datetime(self.setlist_by_song['date'], format='%m/%d/%y').dt.date

        notebook_data = (self.setlist_by_song[self.setlist_by_song['date'] > one_year_ago]
                               ).reset_index(drop=True)[['song_name', 'show_index_overall', 'date','gap']]

        notebook = (
            notebook_data
            .groupby(['song_name'])
            .agg({
                'show_index_overall': ['count', 'max'],
                'gap': ['min', 'max', 'mean', 'median', 'std']
            })
            .reset_index()
            .round(2)
        )
        notebook.columns = ['_'.join(col).strip() for col in notebook.columns.values]

        notebook = notebook.rename(columns={
            'song_name_': 'song', 
            'show_index_overall_count': 'times_played_in_last_year', 
            'show_index_overall_max': 'last_played', 
            'gap_min': 'min_gap', 
            'gap_max': 'max_gap', 
            'gap_mean': 'avg_gap',
            'gap_median': 'med_gap',  
            'gap_std': 'std_gap'
        })
        
        notebook['current_gap'] = self.last_show - notebook['last_played']

        notebook = (
            notebook.merge(
                self.showdata[['show_index_overall', 'date']], left_on='last_played', 
                right_on='show_index_overall', 
                how='left'
                )
            .rename(columns={'date': 'ltp_date'})
            .drop(columns=['show_index_overall', 'last_played'])
            )[['song', 'times_played_in_last_year', 'ltp_date','current_gap', 'avg_gap', 'med_gap']]

        notebook = (
            notebook[(notebook['current_gap'] > 3) & (notebook['song'] != 'Drums')]
            .sort_values(by='times_played_in_last_year', ascending=False)
            .reset_index(drop=True)
        )
                        
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