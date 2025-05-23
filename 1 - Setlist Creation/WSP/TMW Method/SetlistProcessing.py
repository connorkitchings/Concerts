import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

BASE_URL = 'http://everydaycompanion.com/'

# Helper: Convert date string to datetime

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%m/%d/%y')
    except Exception:
        return pd.NaT

def process_dim(st_yr=1986, end_yr=2025):
    tour_list = [y for y in range(st_yr, end_yr + 1) if y != 2004]
    tour_df_list = []
    for year in tour_list:
        yr = str(year)[-2:]
        year_link = f'{BASE_URL}asp/tour{yr}.asp'
        print(f"Scraping: {year_link}")
        try:
            resp = requests.get(year_link)
            resp.encoding = 'latin1'
            soup = BeautifulSoup(resp.text, 'html.parser')
            p = soup.find('p')
            if not p:
                continue
            tour_string = p.get_text()
            tour_string = tour_string.replace('??', '00')
            # Find all dates
            dates = re.findall(r'\d{2}/\d{2}/\d{2}\b\??', tour_string)
            # Split venues by date pattern
            venues = re.split(r'\d{2}/\d{2}/\d{2}\b\??', tour_string)
            venues = [v.strip() for v in venues if v.strip()]
            # Align lengths
            min_len = min(len(dates), len(venues))
            dates = dates[:min_len]
            venues = venues[:min_len]
            tour_data = pd.DataFrame({'date': dates, 'venue': venues})
            tour_data['link'] = [f"{BASE_URL}setlists/" + \
                (datetime.strptime(d, '%m/%d/%y').strftime('%Y%m%d') if parse_date(d) is not pd.NaT else 'NA') + "a.asp" for d in tour_data['date']]
            # Manual fixes (abbreviated for brevity, should be expanded from R version)
            # ... (add any manual link corrections here as needed) ...
            tour_data = tour_data[tour_data['link'] != 'NODATA']
            tour_data = tour_data.drop_duplicates()
            tour_data['date_num'] = tour_data['link'].str.extract(r'(\d{8})')
            tour_data['year'] = tour_data['date_num'].str[:4].astype(float)
            tour_data['month'] = tour_data['date_num'].str[4:6].astype(float)
            tour_data['day'] = tour_data['date_num'].str[6:8].astype(float)
            tour_data['date'] = pd.to_datetime(tour_data[['year', 'month', 'day']], errors='coerce')
            # Venue parsing
            venue_split = tour_data['venue'].str.split(', ')
            tour_data['state'] = venue_split.apply(lambda x: x[-1] if len(x) > 0 else None)
            tour_data['city'] = venue_split.apply(lambda x: x[-2] if len(x) > 1 else None)
            tour_data['venue_name'] = venue_split.apply(lambda x: ', '.join(x[:-2]) if len(x) > 2 else (x[0] if len(x) == 1 else None))
            tour_data['venue_full'] = tour_data['venue'].str.upper()
            tour_data['city'] = tour_data['city'].str.upper()
            tour_data['venue_name'] = tour_data['venue_name'].str.upper()
            tour_data['venue_full'] = tour_data['venue_full'].str.upper()
            # Add more cleaning/mapping as needed
            tour_df_list.append(tour_data)
        except Exception as e:
            print(f"Failed to process {year_link}: {e}")
            continue
    tour_data = pd.concat(tour_df_list, ignore_index=True)
    tour_data = tour_data.sort_values(['year', 'month', 'day']).reset_index(drop=True)
    tour_data['show_index'] = np.arange(1, len(tour_data) + 1)
    return tour_data

def process_setlist(setlist_link):
    setlist_link = setlist_link.lower()
    try:
        resp = requests.get(setlist_link)
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = pd.read_html(resp.text)
        # Table index 5 in R (6th table), Python is 0-based
        setlist_raw = tables[5].copy()
        setlist_raw.columns = ['Raw']
        setlist_raw['Raw'] = setlist_raw['Raw'].astype(str).str.replace('ï', 'i')
        # Set assignment logic
        def assign_set(x):
            if x.startswith('??'):
                return 'Details'
            elif x.startswith('0: '):
                return '0'
            elif x.startswith('1: '):
                return '1'
            elif x.startswith('2: '):
                return '2'
            elif x.startswith('3: '):
                return '3'
            elif x.startswith('4: '):
                return '4'
            elif x.startswith('E: '):
                return 'E'
            elif x.startswith('E1:') or x.startswith('E2:') or x.startswith('E3:'):
                return 'E'
            elif re.match(r'^\d{2}/', x[:3]):
                return 'Details'
            elif x.startswith('*'):
                return 'Song_Notes'
            elif x.startswith('['):
                return 'Show_Notes'
            else:
                return 'Other'
        setlist_raw['set'] = setlist_raw['Raw'].apply(assign_set)
        # Remove set prefixes
        def strip_prefix(row):
            if row['set'] in ['0', '1', '2', '3', '4', 'E']:
                return row['Raw'][3:]
            return row['Raw']
        setlist_raw['Raw'] = setlist_raw.apply(strip_prefix, axis=1)
        # Songs extraction
        songs = setlist_raw[~setlist_raw['set'].isin(['Details', 'Song_Notes', 'Show_Notes', 'Other'])].copy()
        # Split by ',' and ' > '
        songs = songs.assign(Raw=songs['Raw'].str.split(',')).explode('Raw')
        songs['into'] = songs['Raw'].str.contains(' > ')
        songs = songs.assign(Raw=songs['Raw'].str.split(' > ')).explode('Raw')
        songs['song_name'] = songs['Raw'].str.strip().str.upper()
        songs['notes_id'] = songs['song_name'].str.count(r'\*')
        songs['song_notes_key'] = np.where(songs['notes_id'] == 0, '', '*' * songs['notes_id'])
        songs['link'] = setlist_link
        songs['song_name'] = songs['song_name'].str.replace(r'\*', '', regex=True)
        # Manual song name fixes (abbreviated)
        songs['song_name'] = songs['song_name'].replace({
            '???': 'JAM',
            'ARU/WSP JAM': 'JAM',
            'THIS MUST BE THE PLACE (NA<EF>VE MELODY)': 'THIS MUST BE THE PLACE (NAIEVE MELODY)',
            'W<CR>M': 'WURM',
            'LAWYERS': 'LAWYERS GUNS AND MONEY',
            'GUNS': 'LAWYERS GUNS AND MONEY',
            'AND MONEY': 'LAWYERS GUNS AND MONEY',
        })
        songs = songs.drop_duplicates().reset_index(drop=True)
        songs['song_index'] = np.arange(1, len(songs) + 1)
        # Notes extraction
        raw_notes = setlist_raw[setlist_raw['set'].isin(['Song_Notes', 'Show_Notes', 'Other'])].copy()
        # Show notes
        show_notes_df = pd.DataFrame({'link': [setlist_link], 'show_notes': ['']})
        if 'Show_Notes' in raw_notes['set'].values:
            show_notes = raw_notes[raw_notes['set'] == 'Show_Notes']['Raw'].tolist()
            show_notes_df = pd.DataFrame({'link': [setlist_link], 'show_notes': [' '.join(show_notes)]})
        # Song notes
        notes_df = pd.DataFrame({'link': [setlist_link], 'song_notes_key': [np.nan], 'song_note_detail': ['']})
        if 'Song_Notes' in raw_notes['set'].values:
            notes_str = ' '.join(raw_notes[raw_notes['set'] == 'Song_Notes']['Raw'].tolist())
            notessplit = re.split(r'(?<=[A-Za-z])\*', notes_str)
            notessplit = [notessplit[0]] + ['*' + n for n in notessplit[1:]] if len(notessplit) > 1 else notessplit
            notes_df = pd.DataFrame([
                {'link': setlist_link,
                 'song_notes_key': n.split(' ')[0].strip(),
                 'song_note_detail': ' '.join(n.split(' ')[1:]).strip().upper()}
                for n in notessplit if n.strip()
            ])
        # Join notes to songs
        songs = songs.merge(show_notes_df, on='link', how='left')
        songs = songs.merge(notes_df, on=['link', 'song_notes_key'], how='left')
        songs = songs.drop(['song_notes_key', 'notes_id'], axis=1)
        print(f"Loaded setlist: {setlist_link}")
        return songs
    except Exception as e:
        print(f"Failed to process setlist {setlist_link}: {e}")
        return pd.DataFrame()

def load_all_data(start=1986, end=2025):
    tour_data = process_dim(st_yr=start, end_yr=end)
    show_dim = tour_data[tour_data['date'] < pd.Timestamp.now()]
    fut_dim = tour_data[tour_data['date'] >= pd.Timestamp.now()]
    print(f"{len(show_dim)} Historical & {len(fut_dim)} Future Shows Loaded - Now Loading Setlists")
    # Load setlists for historical shows
    songs = pd.concat([process_setlist(link) for link in show_dim['link']], ignore_index=True)
    # Post-process songs
    songs['song_note_detail'] = songs['song_note_detail'].replace('', np.nan)
    songs['show_notes'] = songs['show_notes'].replace('', np.nan)
    songs['set_num'] = np.where(songs['set'] == 'E', '99', songs['set'])
    songs['set'] = pd.to_numeric(songs['set_num'], errors='coerce')
    songs = songs.groupby('link').apply(lambda df: df.assign(min_set=df['set'].min(), max_set=df['set'].max())).reset_index(drop=True)
    songs['set'] = np.where((songs['set'] == 0) & (songs['min_set'] == 0) & (songs['max_set'].isin([99, 0])), 1, songs['set'])
    songs = songs.drop(['min_set', 'max_set', 'set_num'], axis=1)
    songs = songs[['link', 'set', 'song_index', 'song_name', 'into', 'song_note_detail', 'show_notes']]
    # Song fact table
    dim_songs = songs.groupby(['link', 'show_notes']).agg(n_songs=('song_index', 'max')).reset_index()
    songs = songs.drop(['show_notes'], axis=1)
    # Slim future
    Slim_Fut = fut_dim.copy()
    Slim_Fut['is_soundcheck'] = 0
    Slim_Fut['is_opening_act'] = 0
    Slim_Fut['show_notes'] = ''
    Slim_Fut['n_songs'] = 0
    Slim_Fut['weekday'] = Slim_Fut['date'].dt.day_name()
    Slim_Fut['is_fut'] = 1
    Slim_Fut = Slim_Fut.sort_values('date')
    # Dim
    dim = show_dim.merge(dim_songs, on='link', how='left')
    dim['is_radio'] = dim['venue_full'].str.contains(r'\b\d+\.\d+FM\b|\b\d+\.\d\b|NBC STUDIOS|ED SULLIVAN THEATER|STUDIO 6B, ROCKAFELLER CENTER|CNN STUDIOS| STUDIO| RECORD', regex=True).astype(int)
    dim['is_soundcheck'] = dim['show_notes'].fillna('').str.contains(r'\[Soundcheck; ', regex=True).astype(int)
    dim['is_opening_act'] = dim['show_notes'].fillna('').str.lower().str.contains('opened for').astype(int)
    dim['weekday'] = dim['date'].dt.day_name()
    dim['is_fut'] = 0
    dim['n_songs'] = dim['n_songs'].fillna(0)
    dim['show_notes'] = dim['show_notes'].fillna('')
    dim = pd.concat([dim, Slim_Fut], ignore_index=True)
    print(f"Successfully Loaded {dim['link'].nunique()} Widespread Panic Shows ({len(songs)} Total Songs) from {dim['year'].min()} to {dim['year'].max()}")
    return [songs, dim[dim['is_fut'] == 0], dim[dim['is_fut'] == 1]]
