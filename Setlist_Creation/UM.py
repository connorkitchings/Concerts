from typing import Tuple
from SetlistCollector import SetlistCollector
from datetime import datetime, date
import requests
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
from io import StringIO
import logging
import json
import os

SONG_TABLE_IDX = 1
VENUE_TABLE_IDX = 0

class UMSetlistCollector(SetlistCollector):
    """Scraper for Umphrey's McGee show data using allthings.umphreys.com."""

    def __init__(self):
        """Initialize UMSetlistCollector."""
        super().__init__(band="UM")
        self.base_url = "https://allthings.umphreys.com"
        
    def load_song_data(self) -> pd.DataFrame:
        """
        Load and return song list data from allthings.umphreys.com as a DataFrame.
        """
        songlist_url = f"{self.base_url}/song/"
        response = requests.get(songlist_url)
        response.raise_for_status()

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')

        if not tables or len(tables) <= SONG_TABLE_IDX:
            logging.error(f"Expected song table at index {SONG_TABLE_IDX} not found in UM song page.")
            return pd.DataFrame()
        tables_str = str(tables)
        tables_io = StringIO(tables_str)
        tables = pd.read_html(tables_io)

        songlist_data = tables[SONG_TABLE_IDX].copy().sort_values(by='Song Name').reset_index(drop=True)
        songlist_data['Debut Date'] = pd.to_datetime(songlist_data['Debut Date']).dt.date
        songlist_data['Last Played'] = pd.to_datetime(songlist_data['Last Played']).dt.date

        return songlist_data
    
    def load_show_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load and return venue data from allthings.umphreys.com.
        Returns a tuple: (empty DataFrame for show data, DataFrame for venue data).
        """
        venues_url = f"{self.base_url}/venues/"
        response = requests.get(venues_url)
        response.raise_for_status()

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')

        if not tables or len(tables) <= VENUE_TABLE_IDX:
            logging.error(f"Expected venue table at index {VENUE_TABLE_IDX} not found in UM venue page.")
            return pd.DataFrame(), pd.DataFrame()
        tables_str = str(tables)
        tables_io = StringIO(tables_str)
        tables = pd.read_html(tables_io)

        venue_data = tables[VENUE_TABLE_IDX].copy().reset_index(names='id')
        venue_data['id'] = venue_data['id'].astype(str)
        venue_data['Last Played'] = pd.to_datetime(venue_data['Last Played']).dt.date

        # Return empty DataFrame for show_data to match abstract method signature
        show_data = pd.DataFrame()

        return show_data, venue_data
    
    def create_setlist_data(self) -> pd.DataFrame:
        """
        Load all setlist data from allthings.umphreys.com.
        
        Returns:
            DataFrame for setlist data.
        """
        songlist_url = f"{self.base_url}/song/"
        response = requests.get(songlist_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        
        if tables:
            tables_str = str(tables)
            
        # Extract song names using regex
        pattern = r'href="/song/([^"]+)"'
        song_names = re.findall(pattern, tables_str)

        setlists = []
        for song in song_names:
            song_url = songlist_url + song
            response = requests.get(song_url)
            response.raise_for_status()
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            title = re.search(r'"(.*?)"', title_tag.get_text()).group(1) if title_tag and '"' in title_tag.get_text() else 'Unknown Title'
            tables = soup.find_all('table')
            if not tables or len(tables) == 0:
                logging.warning(f"No tables found for song {song} at {song_url}")
                continue
            tables_str = str(tables)
            tables_io = StringIO(tables_str)
            tables = pd.read_html(tables_io)
            song_table = tables[0].copy().sort_values(by='Date Played').reset_index(drop=True)
            song_table.insert(0, 'Song Name', title)
            song_table['Date Played'] = pd.to_datetime(song_table['Date Played']).dt.date
            if 'Show Gap' in song_table.columns:
                song_table = song_table.drop(columns=['Show Gap'])
            setlists.append(song_table)
        if not setlists:
            logging.error("No setlists could be parsed from UM song pages.")
            return pd.DataFrame()
        setlist_data = pd.concat(setlists).reset_index(drop=True)
        setlist_data['Footnote'] = setlist_data['Footnote'].fillna('')
        setlist_data = setlist_data.sort_values(by=['Date Played', 'Song Name'], ascending=[False, True]).reset_index(drop=True)
        self.update_last_updated()  # Update timestamp
        # Save last_updated to a json file in the data directory
        os.makedirs(self.data_dir, exist_ok=True)
        with open(os.path.join(self.data_dir, 'last_updated.json'), 'w') as f:
            json.dump({'last_updated': self.last_updated}, f)
        return setlist_data
    
    def update_setlist_data(self, venue_data: pd.DataFrame) -> pd.DataFrame:
        """
        Update existing setlist data with new shows.
        
        Args:
            venue_data: Venue data DataFrame.
            
        Returns:
            Updated DataFrame containing setlist data.
        """
        try:
            # Load existing setlist data
            existing_setlist_data = pd.read_csv(self.data_dir / 'setlistdata.csv')
            # Use maximum date played to filter venue data for missing shows
            last_show = datetime.strptime(existing_setlist_data['Date Played'].max(), '%Y-%m-%d').date()
            existing_setlist_data['Date Played'] = pd.to_datetime(existing_setlist_data['Date Played']).dt.date
        except (FileNotFoundError, pd.errors.EmptyDataError):
            logging.warning("No existing setlist data found.")
            return None  # Return None to indicate update is not possible
        
        missing_setlists_venues = venue_data[
            (venue_data['Last Played'] > last_show) & 
            (venue_data['Last Played'] < datetime.today().date())
        ].copy().reset_index(drop=True)
        
        # Adjust the venue name for entries including special characters or ending with ", The"
        missing_setlists_venues['Venue Name'] = missing_setlists_venues['Venue Name'].apply(
            lambda x: ('The ' + x[:-5] if x.endswith(', The') else x).replace('&', 'amp').replace("'", '039').replace("!", '')
        )
        
        new_setlists = []
        for _, row in missing_setlists_venues.iterrows():
            base_venue_url = f"{self.base_url}/venues/"
            components = []
            venue_name = row['Venue Name']
            city = row['City']
            state = row['State']
            country = row['Country']
            
            if pd.notna(venue_name) and venue_name != '':
                components.append(venue_name.replace(' ', '-').lower())
            if pd.notna(city) and city != '':
                components.append(city.replace(' ', '-').lower())
            if pd.notna(state) and state != '':
                components.append(state.replace(' ', '-').lower())
            if pd.notna(country) and country != '':
                components.append(country.replace(' ', '-').lower())
                
            venue_url = base_venue_url + '-'.join(components)
            
            # Check Venue Page for all dates needed
            try:
                response = requests.get(venue_url)
                response.raise_for_status()
                
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                tables = soup.find_all('table')
                
                if tables:
                    tables_str = str(tables)
                    tables_io = StringIO(tables_str)
                    tables = pd.read_html(tables_io)
                    
                venue_table = tables[0].copy()
                relevant_dates = [date for date in pd.to_datetime(venue_table['Date'], errors='coerce').dt.date 
                                 if pd.notna(date) and date > last_show]
                
                for show_date in relevant_dates:
                    date_url = show_date.strftime('%B-%-d-%Y').lower()
                    base_setlist_url = f"{self.base_url}/setlists/umphreys-mcgee-"
                    url_components = [date_url]
                    
                    if pd.notna(venue_name) and venue_name != '':
                        url_components.append(venue_name.replace(' ', '-').lower())
                    if pd.notna(city) and city != '':
                        url_components.append(city.replace(' ', '-').lower())
                    if pd.notna(state) and state != '':
                        url_components.append(state.replace(' ', '-').lower())
                    if pd.notna(country) and country != '':
                        url_components.append(country.replace(' ', '-').lower())
                        
                    setlist_url = base_setlist_url + '-'.join(url_components) + '.html'
                    new_setlist = self._get_setlist_from_url(setlist_url, show_date)
                    new_setlist['Venue'] = f"{venue_name}, {city}, {state}"
                    new_setlists.append(new_setlist)
            except Exception as e:
                print(f"Error processing venue {venue_name}: {e}")
           
        if new_setlists:
            new_setlists = pd.concat(new_setlists).reset_index(drop=True)
            new_setlists = new_setlists[['Song Name', 'Date Played', 'Venue', 'Set', 'Song Before', 'Song After', 'Footnote']]
            new_setlists = new_setlists.sort_values(by=['Date Played', 'Song Name'], ascending=[False, True]).reset_index(drop=True)
            
            # Clean up venue names
            new_setlists['Venue'] = new_setlists['Venue'].str.replace(r'\bamp\b', '&', regex=True)
            new_setlists['Venue'] = new_setlists['Venue'].str.replace('039', "'", regex=False)
            
            # Fix specific venue name issues
            venue_replacements = {
                "Express Live, Columbus, OH": "Express Live!, Columbus, OH",
                "Kemba Live, Columbus, OH": "KEMBA Live!, Columbus, OH",
                "Ram's Head Live, Baltimore, MD": "Ram's Head Live!, Baltimore, MD",
                "Virginia Credit Union Live, Richmond, VA": "Virginia Credit Union Live!, Richmond, VA"
            }
            
            for old_name, new_name in venue_replacements.items():
                new_setlists['Venue'] = np.where(new_setlists['Venue'] == old_name, new_name, new_setlists['Venue'])
                
            # Handle 'The' in venue names
            new_setlists['Venue'] = new_setlists['Venue'].apply(lambda x: x[:-4] if x.strip().casefold().endswith('the') else x)
            
            # Combine with existing data
            final_setlist = pd.concat([existing_setlist_data, new_setlists]).sort_values(
                by=['Date Played', 'Song Name'], ascending=[False, True]).reset_index(drop=True)
        else:
            final_setlist = existing_setlist_data
            
        final_setlist['Footnote'] = final_setlist['Footnote'].fillna('')
        
        return final_setlist
    
    def _get_setlist_from_url(self, url: str, show_date: date) -> pd.DataFrame:
        """
        Extract setlist data from a specific URL.

        Args:
            url: URL to the setlist page.
            show_date: Date of the show.

        Returns:
            DataFrame containing setlist data for the show.
        """
        response = requests.get(url)
        response.raise_for_status()

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        setlist_body = soup.find('div', class_='setlist-body')
        
        if not setlist_body:
            print(f"Warning: Could not find setlist body in {url}")
            return pd.DataFrame()  # Return empty DataFrame

        footnotes_dict = {}
        footnotes_section = soup.find('p', class_='setlist-footnotes')

        if footnotes_section:
            footnote_text = footnotes_section.get_text()
            footnote_matches = re.findall(r'\[(\d+)\](.*?)(?=\[\d+\]|$)', footnote_text, re.DOTALL)
            for num, desc in footnote_matches:
                footnotes_dict[num] = desc.strip()

        all_songs = []
        current_set = ""

        for paragraph in setlist_body.find_all('p'):
            set_label = paragraph.find('b', class_='setlabel')
            if set_label:
                current_set = set_label.get_text().strip()

            song_boxes = paragraph.find_all('span', class_='setlist-songbox')

            set_songs = []
            for i, box in enumerate(song_boxes):
                song_link = box.find('a')
                song_name = song_link.get_text().strip() if song_link else box.get_text().strip()
                song_name = re.sub(r'[,>]$', '', song_name).strip()

                footnote_refs = [re.search(r'\[(\d+)\]', sup.get_text()).group(1)
                                for sup in box.find_all('sup')
                                if re.search(r'\[(\d+)\]', sup.get_text())]

                footnote_text = ' '.join(footnotes_dict.get(ref, '') for ref in footnote_refs).strip()

                set_songs.append({
                    'Song Name': song_name,
                    'Set': current_set,
                    'Footnote': footnote_text.strip(),
                })

            for i, song_data in enumerate(set_songs):
                prev_song = set_songs[i-1]['Song Name'] if i > 0 else '***'
                next_song = set_songs[i+1]['Song Name'] if i < len(set_songs) - 1 else '***'

                song_data['Song Before'] = prev_song
                song_data['Song After'] = next_song

                all_songs.append(song_data)

        df = pd.DataFrame(all_songs)

        df['Set'] = np.where(df['Set'].str.contains('Encore'), 'e',
                            np.where(df['Set'].str.contains('Set 1'), '1',
                                    np.where(df['Set'].str.contains('Set 2'), '2',
                                            np.where(df['Set'].str.contains('Set 3'), '3', df['Set']))))

        df['Date Played'] = show_date
        df['Date Played'] = pd.to_datetime(df['Date Played']).dt.date

        return df
    
    def load_setlist_data(self, method='Update') -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load setlist data using the specified method.
        
        Args:
            method: Method to use for loading setlist data ('All' or 'Update').
            
        Returns:
            Tuple containing (DataFrame for setlist data, empty DataFrame for transitions).
        """
        # Get venue data for update method
        _, venue_data = self.load_show_data()
        
        if method == 'All':
            setlist_data = self.create_setlist_data()
        elif method == 'Update':
            setlist_data = self.update_setlist_data(venue_data)
            if setlist_data is None:
                logging.info("Switching to 'All' method since update is not possible.")
                setlist_data = self.create_setlist_data()
        else:
            raise ValueError(f"Invalid method: {method}. Use 'All' or 'Update'.")
        
        # Empty DataFrame for transitions to match abstract method signature
        transition_data = pd.DataFrame()
        
        return setlist_data, transition_data
    
    def create_and_save_data(self) -> None:
        """Save UM data to CSV files in the data directory."""
        
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
                'venuedata.csv': venue_data,
                'setlistdata.csv': setlist_data,
            }
            
            # Save each file
            logging.info("Saving data.")
            for filename, data in data_pairs.items():
                filepath = self.data_dir / filename
                data.to_csv(filepath, index=False)
        
        except Exception as e:
            print(f"Error saving UM data: {e}")
        # Save last_updated timestamp to a json file in the data directory
        self.update_last_updated()
        os.makedirs(self.data_dir, exist_ok=True)
        with open(os.path.join(self.data_dir, 'last_updated.json'), 'w') as f:
            json.dump({'last_updated': self.last_updated}, f)