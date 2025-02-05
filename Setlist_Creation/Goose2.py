import json
import pandas as pd
import numpy as np
from datetime import datetime, date
from bs4 import BeautifulSoup
from io import StringIO
import os
import sys
import requests

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()
base_dir = os.path.dirname(script_dir)

class GooseDataScraper:
    """
    Data scraper for Goose band data collection.
    """
    
    def __init__(self, 
                 start_year: int = 2016,  # Goose's founding year
                 end_year: int = None, 
                 scrape_mode: str = 'update'):
        """
        Initialize Goose data scraper.
        """
        self.band_name = "Goose"
        self.start_year = start_year
        self.end_year = end_year or date.today().year
        self.scrape_mode = scrape_mode
        
        # Base URLs for API endpoints
        self.base_url = "https://elgoose.net/api/v2"
        self.base_url_v1 = "https://elgoose.net/api/v1"
        
        # Today's date for filtering
        self.today = datetime.today().strftime('%Y-%m-%d')
        
        # Set up data directory
        self.data_dir = os.path.join(base_dir, "Data", "Goose")

    def load_show_dates(self):
        """Load show dates from Goose API."""
        showlist_url = f"{self.base_url}/shows.json?order_by=showdate"
        showlistdata_json = requests.get(showlist_url).json()
        showlist_df = pd.DataFrame(showlistdata_json['data'])
        
        past_df = showlist_df[showlist_df['showdate'] < self.today]
        future_df = showlist_df[showlist_df['showdate'] >= self.today].sort_values('showdate').head(1)
        result = pd.concat([past_df, future_df])
        goose_showlist_df = result[(result['artist'] == 'Goose')].copy().reset_index(drop=True)
        goose_showlist_df['link'] = goose_showlist_df['show_id'].astype(str)
        
        return goose_showlist_df

    def load_song_codes(self):
        """Load song data from Goose API."""
        songlist_url_api = f"{self.base_url}/songs.json?order_by=name"
        songlistdata_json = requests.get(songlist_url_api).json()
        song_df = pd.DataFrame(songlistdata_json['data'])
        songdata_og = song_df.drop(columns=['slug','created_at','updated_at'])
        
        songlist_url = "https://elgoose.net/song/"
        response = requests.get(songlist_url)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')
        
        if tables:
            tables_str = str(tables)
            tables_io = StringIO(tables_str)
            tables = pd.read_html(tables_io)
            songdata_info = tables[1].copy()
        
        songdata = songdata_og.merge(songdata_info, left_on="name", right_on="Song Name", how="inner")[
            ['id','Song Name', 'isoriginal','Original Artist', 'Debut Date','Last Played',
             'Times Played Live', 'Avg Show Gap']
        ]
        
        songdata = songdata.rename(columns={
            'Song Name': 'song_name', 
            'Original Artist': 'original_artist', 
            'Debut Date': 'debut_date', 
            'Last Played': 'last_played', 
            'Times Played Live': 'times_played_live', 
            'Avg Show Gap': 'avg_show_gap'
        })
        
        return songdata

    def load_setlists(self, link_list=None, method='update'):
        """Load setlist data from Goose API."""
        setlist_url = f"{self.base_url_v1}/setlists.json?order_by=showdate"
        setlistdata_json = requests.get(setlist_url).json()
        setlist_df = pd.DataFrame(setlistdata_json['data'])
        
        transitiondata = setlist_df[
            ['transition_id', 'transition']
            ].drop_duplicates().sort_values(by=['transition_id'], ascending=True).reset_index(drop=True)
        
        setlistdata = setlist_df[setlist_df['artist'] == "Goose"].copy().reset_index(drop=True)[
            ['uniqueid', 'show_id', 'song_id','setnumber','position','tracktime','transition_id',
             'isreprise','isjam','footnote','isjamchart','jamchart_notes','soundcheck',
             'isverified','isrecommended']
        ]
        
        return setlistdata, transitiondata

    def save_data(self, show_list=None, song_data=None, setlist_data=None, transitiondata=None):
        """Save collected data to CSV files."""
        if show_list is None and song_data is None and setlist_data is None:
            return
        
        if show_list is not None:
            venuedata = show_list[
                ['venue_id', 'venuename', 'location', 'city', 'state', 'country']
            ].drop_duplicates().sort_values(by=['venue_id'], ascending=True).reset_index(drop=True)
            
            tourdata = show_list[['tour_id', 'tourname']].drop_duplicates().sort_values(by=['tour_id'], ascending=True).reset_index(drop=True)
            
            processed_showdata = show_list[
                ['show_id', 'showdate', 'showtitle', 'venue_id', 'tour_id']
            ].copy().sort_values(by=['showdate'], ascending=True).reset_index(names='show_number').assign(show_number=lambda x: x['show_number'] + 1)
            processed_showdata['showtitle'] = processed_showdata['showtitle'].replace('', None)
            
            venuedata.to_csv(os.path.join(self.data_dir, "venuedata.csv"), index=False)
            tourdata.to_csv(os.path.join(self.data_dir, "tourdata.csv"), index=False)
            processed_showdata.to_csv(os.path.join(self.data_dir, "showdata.csv"), index=False)
        
        if song_data is not None:
            song_data.to_csv(os.path.join(self.data_dir, "songdata.csv"), index=False)
            
        if setlist_data is not None:
            setlist_data.to_csv(os.path.join(self.data_dir, "setlistdata.csv"), index=False)
            transitiondata.to_csv(os.path.join(self.data_dir, "transitiondata.csv"), index=False)

def main():
    """Main function to run Goose data scraper."""
    scraper = GooseDataScraper(scrape_mode='update')
    
    show_list = scraper.load_show_dates()
    song_data = scraper.load_song_codes()
    setlist_data, transitiondata = scraper.load_setlists()
    
    scraper.save_data(show_list, song_data, setlist_data, transitiondata)
    print("Goose data scraping completed successfully.")

if __name__ == "__main__":
    main()