from typing import Tuple, Optional
from SetlistCollector import SetlistCollector
from pathlib import Path
from datetime import datetime, date
import requests
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
from io import StringIO

class WSPSetlistCollector(SetlistCollector):
    """Scraper for Widespread Panic show data. """

    def __init__(self):
        """
        Initialize WSPSetlistCollector.
        
        """
        super().__init__(band='WSP')
        # Set start year and end year
        self.start_year = 1985
        self.this_year = datetime.today().year
        
        # Set today's date
        self.today = date.today()
        
        # Define comma songs and dictionary 
        self.comma_songs = ['Guns', 'And Money', 'Let Me Follow You Down', 'Let Me Hold Your Hand', 
                          "Please Don't Go", 'Rattle', 'And Roll', 'Narrow Mind', 'Woman Smarter']
        self.comma_songs_completer = {
            'Lawyers': 'Lawyers Guns And Money',
            'Baby': 'One of the 3 Baby Songs',
            'Shake': 'Shake, Rattle, And Roll',
            'Weak Brain': 'Weak Brain, Narrow Mind',
            'Man Smart': 'Man Smart, Woman Smarter'
        }
        
        # Set url
        self.base_url = 'http://www.everydaycompanion.com/'
        
        # Set up link_list
        self.link_list = []
        
    def load_show_data(self):
        tour_list = [x for x in range(self.start_year, self.this_year + 1) if x != 2004]
        tour_df_list = pd.DataFrame()

        for yr in tour_list:
            yr_str = str(yr)[-2:]
            year_link = f"{self.base_url}asp/tour{yr_str}.asp"
            response = requests.get(year_link)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            try:
                tour_string = soup.find('p').get_text()
            except:
                print(f"No data on Everyday Companion for {yr}.")
                break  
            tour_string = re.sub(r'\?\?', '00', tour_string)

            # Split the string into individual dates
            venues = [venue.strip() for venue in re.split(r'\d{2}/\d{2}/\d{2}', tour_string) if venue.strip()]
            dates = re.findall(r'\d{2}/\d{2}/\d{2}', tour_string)

            tour_data = pd.DataFrame({
                'date': dates,
                'venue': venues
            })

            tour_data['link_date'] = tour_data['date'].apply(lambda x: str(x[6:])+str(x[0:2])+str(x[3:5]))
            for index, value in tour_data['link_date'].items():
                if value[0] in ['8', '9']:
                    tour_data.at[index, 'link_date'] = '19' + value
                if value[0] in ['0', '1', '2']:
                    tour_data.at[index, 'link_date'] = '20' + value
                    
            tour_data['date_count'] = tour_data.groupby('link_date').cumcount() + 1
            tour_data['assigned_letter'] = tour_data['date_count'].apply(lambda x: chr(ord('a') + x - 1))
            tour_data['link'] = self.base_url+'setlists/'+tour_data['link_date']+tour_data['assigned_letter']+'.asp'
            tour_data.drop(columns=['date_count','assigned_letter'], inplace=True)

            tour_data['running_count'] = tour_data.groupby(['date', 'venue']).cumcount() + 1
            
            # Extract year, month, day from link
            tour_data[['year', 'month', 'day']] = tour_data['link'].str.extract(r'(\d{4})(\d{2})(\d{2})')
            tour_data['date_ec'] = tour_data['date']
            tour_data['date'] = pd.to_datetime(tour_data['date'], format='%m/%d/%y', errors='coerce').fillna(pd.NaT)
            tour_data['weekday'] = pd.to_datetime(tour_data['date'], errors='coerce').dt.strftime('%A')

            # Split venue information
            tour_data[['venue_name', 'city', 'state']] = tour_data['venue'].str.rsplit(', ', n=2, expand=True)
            tour_data['city'] = tour_data['city'].str.upper()
            tour_data['venue_name'] = tour_data.apply(lambda row: row['venue_name'] if pd.notna(row['venue_name']) else ', '.join(row[:-2]), axis=1)
            tour_data[['city', 'venue_name']] = tour_data[['city', 'venue_name']].apply(lambda col: col.str.upper())
            tour_data.rename(columns={'venue':'venue_full', 'venue_name':'venue'},inplace=True)
            tour_data['venue_full'] = tour_data['venue_full'].str.upper()

            tour_data.drop(columns=['link_date', 'running_count'], inplace=True)
            tour_data['show_index_withinyear'] = tour_data.index + 1
            tour_df_list = pd.concat([tour_df_list, tour_data])
            
        # Combine DataFrames From Loop List
        combined_tour_data = tour_df_list.reset_index(drop=True)
        combined_tour_data['show_index_overall'] = combined_tour_data.index + 1

        combined_tour_data['date_ec'] = combined_tour_data.apply(lambda row: f'??/{row["day"]}/{row["year"][-2:]}' if row['month'] == '00' else row['date_ec'],axis=1)
        combined_tour_data['date_ec'] = combined_tour_data.apply(lambda row: f'{row["month"]}/??/{row["year"][-2:]}' if row['day'] == '00' else row['date_ec'],axis=1)
        combined_tour_data['date_ec'] = combined_tour_data.apply(lambda row: f'??/??/{row["year"][-2:]}' if ((row['month'] == '00')&(row['day'] == '00')) else row['date_ec'],axis=1)

        combined_tour_data.sort_values(by=['show_index_overall','venue']).reset_index(drop=True, inplace=True)
        mask = (combined_tour_data['venue'] != combined_tour_data['venue'].shift(1)) | (combined_tour_data['show_index_overall'] != combined_tour_data['show_index_overall'].shift(1) + 1)
        combined_tour_data['run_index'] = mask.cumsum()

        combined_tour_data = combined_tour_data[['date','year','month','day','weekday', 'date_ec','venue','city','state','show_index_overall', 'show_index_withinyear', 'run_index', 'venue_full','link']]
        
        venue_conditions = [
        (combined_tour_data['venue'] == 'ADAMS CENTER') & (combined_tour_data['state'] == 'MT'),
        (combined_tour_data['venue'] == 'AUDITORIUM THEATRE') & (combined_tour_data['city'] == 'CHICAGO'),
        (combined_tour_data['venue'] == 'BAYFRONT ARENA') & (combined_tour_data['state'] == 'FL'),
        (combined_tour_data['venue'] == "FLEET PAVILION") & (combined_tour_data['city'] == 'BOSTON'),
        (combined_tour_data['venue'] == "CAESAR'S TAHOE SHOWROOM") & (combined_tour_data['state'] == 'NV')
        ]

        venue_replacements = [
            'ADAMS FIELDHOUSE, UNIVERSITY OF MONTANA',
            'AUDITORIUM THEATER, ROOSEVELT UNIVERSITY',
            'BAYFRONT AUDITORIUM',
            "CAESAR'S TAHOE",
            "CAESAR'S TAHOE"
            ]
        
        # Define conditions and corresponding replacements for city
        city_conditions = [
            (combined_tour_data['venue'] == '23 EAST CABARET') & (combined_tour_data['state'] == 'PA'),
            (combined_tour_data['venue'] == "CAESAR'S TAHOE"),
            (combined_tour_data['venue'] == 'CYNTHIA WOODS MITCHELL PAVILLION'),
            (combined_tour_data['city'].isin(['N. LITTLE ROCK', 'NORTH LITTLE ROCK'])),
            (combined_tour_data['city'] == 'MT. CRESTED BUTTE'),
            (combined_tour_data['city'] == 'SNOWMASS VILLAGE'),
            (combined_tour_data['city'] == 'ELON COLLEGE'),
            (combined_tour_data['city'] == 'N. MYRTLE BEACH')
            ]

        city_replacements = [
            'PHILADELPHIA',
            'LAKE TAHOE',
            'THE WOODLANDS',
            'LITTLE ROCK',
            'CRESTED BUTTE',
            'SNOWMASS',
            'ELON',
            'MYRTLE BEACH'
            ]
        
        # Use np.select to apply the conditions and replacements for venue and city
        combined_tour_data['venue'] = np.select(venue_conditions, venue_replacements, default=combined_tour_data['venue'])
        combined_tour_data['city'] = np.select(city_conditions, city_replacements, default=combined_tour_data['city'])

        # Convert 'date' to datetime format (without immediately formatting back to string)
        combined_tour_data['date'] = pd.to_datetime(combined_tour_data['date'], format='%m-%d-%y', errors='coerce')

        # Get today's date

        # Find the first future date (including today)
        future_dates = combined_tour_data[combined_tour_data['date'].dt.date >= self.today].dropna(subset=['date'])
        first_future_date = future_dates['date'].min()

        # Keep all past shows and only the first future show
        if not pd.isna(first_future_date):
            combined_tour_data = combined_tour_data[(combined_tour_data['date'] <= first_future_date)]

        # Convert back to string format for display
        combined_tour_data['date'] = combined_tour_data['date'].dt.strftime('%m/%d/%y')

        return combined_tour_data

    def load_song_data(self):
        songcode_url = f"{self.base_url}asp/songcode.asp"
        response = requests.get(songcode_url)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')

        if tables:
            tables_str = str(tables)  # Convert tables to string
            tables_io = StringIO(tables_str)  # Wrap in StringIO
            tables = pd.read_html(tables_io)
        song_codes = tables[3].copy()

        # Set the first row as header
        song_codes.columns = song_codes.iloc[0]  # Assign first row as header
        song_codes = song_codes[1:].reset_index(drop=True)  # Drop the first row and reset

        song_codes = song_codes.rename(columns={'Code':'code','Title':'song', 'First': 'ftp', 'Last': 'ltp', 'Times Played': 'times_played', 'Also Known As': 'aka'})
        column = song_codes.pop('song')
        song_codes.insert(0, 'song', column)

        song_codes = song_codes.astype({
            'song': str,
            'code': str,
            'times_played': int
        })
        song_codes['aka'] = song_codes['aka'].fillna('').astype(str)
        # Convert 'ftp' and 'ltp' to datetime and format as mm/dd/yyyy
        song_codes['ftp'] = pd.to_datetime(song_codes['ftp'], format='%m/%d/%y', errors='coerce').dt.strftime('%m/%d/%y')
        song_codes['ltp'] = pd.to_datetime(song_codes['ltp'], format='%m/%d/%y', errors='coerce').dt.strftime('%m/%d/%y')
        return song_codes

    def get_setlist_from_link(self, setlist_link):
        response = requests.get(setlist_link)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')
        if tables:
            tables_str = str(tables)  # Convert tables to string
            tables_io = StringIO(tables_str)  # Wrap in StringIO
            tables = pd.read_html(tables_io)
        setlist_raw = tables[4].copy()
        setlist_raw['Raw'] = setlist_raw[0].str.replace("ï", "i")
        setlist_raw['set'] = setlist_raw['Raw'].apply(lambda x: x[:3] if x[:2] in (['0:', '1:', '2:', '3:', '4:', 'E:','E1','E2','E3','E4']) else 'Notes')
        setlist_raw['set'] = setlist_raw['set'].apply(lambda x: 'Details' if x[:2] == '??'or re.match(r"^\d{2}/", x[:2]) else x)
        setlist_raw['set'] = setlist_raw['set'].str.strip()
        setlist_raw['Raw'] = setlist_raw['Raw'].str.lstrip()
        setlist_raw['Raw'] = np.where(setlist_raw['set'].isin(['0', '1', '2', '3', '4', 'E']), setlist_raw['Raw'].str.replace("^.{3}", "", regex=True), setlist_raw['Raw'])

        songs1 = setlist_raw[~setlist_raw['set'].isin(['Details', 'Notes'])].copy()
        songs1['Raw'] = songs1['Raw'].str.replace('>', ',>', regex=False)
        songs1['Raw'] = songs1['Raw'].str.split(',')
        songs2 = songs1.explode('Raw').copy()
        songs2['into'] = songs2['Raw'].apply(lambda x: 1 if '>' in x else 0)
        songs2['Raw'] = songs2['Raw'].str.replace('>', '', regex=False)
        songs2['Raw'] = songs2['Raw'].str.lstrip()
        songs2['Raw'] = songs2['Raw'].replace('|'.join(songs2['set']), '', regex=True)
        songs3 = songs2[~songs2['Raw'].str.contains('|'.join(self.comma_songs))].copy()
        songs3['Raw'] = songs3['Raw'].map(self.comma_songs_completer).fillna(songs3['Raw'])
        songs3['song_name'] = songs3['Raw'].str.capitalize().str.strip()
        songs3['notes_id'] = songs3['song_name'].str.count(r"\*")
        songs3['song_notes_key'] = np.where(songs3['notes_id'] == 0, "", songs3['notes_id'].apply(lambda x: '*' * x))
        songs4 = songs3.reset_index(drop=True).copy()
        songs4['song_index_show'] = songs4.index + 1
        songs4['song_index_set'] = songs4.groupby('set').cumcount() + 1
        songs = songs4[['set','song_name','into','song_index_show','song_index_set','song_notes_key','notes_id']].copy()
        songs['link'] = str(setlist_link)

        songs['song_name'] = songs['song_name'].str.upper().str.replace('*', '', regex=False)
        conditions = [songs['song_name'].isin(['???', 'ARU/WSP JAM']),songs['song_name'] == 'THIS MUST BE THE PLACE (NA<EF>VE MELODY)',songs['song_name'] == 'W<CR>M']
        replacements = ['JAM','THIS MUST BE THE PLACE (NAIEVE MELODY)','WURM']
        songs['song_name'] = np.select(conditions, replacements, default=songs['song_name'])

        songs = songs[['song_name', 'set','song_index_set','song_index_show','into','song_notes_key',\
                        'notes_id', 'link']]

        is_notes = songs['notes_id'].sum()
        if is_notes > 0:
            try:
                notes_df = setlist_raw.loc[setlist_raw['set'].isin(['Notes'])].loc[:, ['Raw']]
                notes_str_series = notes_df['Raw'].iloc[1]
                notes_split = re.split(r'(\*+|\[)', notes_str_series)
                notes_split = [s for s in notes_split if s]
                notes_split = [s for s in notes_split if s.startswith(' ') or s.startswith('*')]
                notes_df = pd.DataFrame({'song_notes_key': notes_split[::2], 'song_note_detail': notes_split[1::2]})
                if setlist_link=="http://everydaycompanion.com/setlists/20091017a.asp":
                    notes_df = pd.DataFrame({'song_notes_key':['*'], 'song_note_detail':['with The Allman Brothers']})
                if setlist_link=="http://everydaycompanion.com/setlists/20161030a.asp":
                    notes_df = pd.DataFrame({'song_notes_key':['*'], 'song_note_detail':['Steve Lopez on Percussion']})
                    notes_df['song_note_detail'] = notes_df['song_note_detail'].str.lstrip()
                songs_final = pd.merge(songs, notes_df, how='left', left_on='song_notes_key', right_on='song_notes_key')
                songs_final.drop(columns=['song_notes_key', 'notes_id'], inplace=True)
            except AttributeError as notes_error:
                songs_final = songs.copy()
                songs_final['song_note_detail'] = ''
        else:
            songs_final = songs.copy()
            songs_final = songs_final.assign(song_note_detail='')
        songs_final = songs_final.reset_index(drop=True)
        return songs_final

    def load_setlist_data(self, link_list, method='update'):
        if method == 'all':
            print("Loading all WSP Setlist Data")
            all_setlists = pd.DataFrame()
            for link in link_list:
                link_setlist = self.get_setlist_from_link(link)
                all_setlists = pd.concat([all_setlists, link_setlist]).reset_index(drop=True)
        
        elif method == 'update':
            print("Updating Existing WSP Setlist Data")
            
            all_setlists = pd.read_csv((self.data_dir / "setlistdata.csv"))
            filtered_link_list = [link for link in link_list if str(self.this_year) in link.split('/')[-1] or str(self.this_year - 1)  in link.split('/')[-1]]
            
            for link in filtered_link_list:
                link_setlist = self.get_setlist_from_link(link)
                all_setlists = pd.concat([all_setlists, link_setlist])
                all_setlists = all_setlists.drop_duplicates(subset=['link', 'song_name', 'set', 'song_index_show', 'song_index_set']).reset_index(drop=True)

        return all_setlists
    
    def create_and_save_data(self) -> None:
        """Save WSP data to CSV files in the data directory."""
        
        print(f"Loading Song Data")
        song_data = self.load_song_data()
        print(f"Loading Show Data")
        show_data = self.load_show_data()
        self.link_list = show_data.link.unique()
        setlist_data = self.load_setlist_data(self.link_list, method = 'update')
    
        try:
            # Define files to save
            data_pairs = {
                'songdata.csv': song_data,
                'showdata.csv': show_data,
                'setlistdata.csv': setlist_data
            }
            
            # Save each file
            print("Saving data.")
            for filename, data in data_pairs.items():
                filepath = self.data_dir / filename
                data.to_csv(filepath, index=False)
        
        except Exception as e:
            print(f"Error saving Widespread Panic data: {e}")
        