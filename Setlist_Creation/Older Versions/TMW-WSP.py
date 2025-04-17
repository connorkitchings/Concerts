# %%
import os
import pandas as pd
import numpy as np
import time
import datetime
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
import pickle
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# %% [markdown]
# # Lists and Dictionaries

# %%
# Change Unknown Dates To Update Links
special_cases = {
    ('00/00/85', 'A-Frame, Weymanda Court, Athens, GA'): 'http://everydaycompanion.com/setlists/19850000a.asp',
    ('00/00/86', 'Phi Delta Theta House, University of Georgia, Athens, GA'): 'NODATA',
    ('00/00/86', '** UNKNOWN **, ** UNKNOWN **, UU'): 'NODATA',
    ('03/00/86', 'Uptown Lounge, Athens, GA'): 'http://everydaycompanion.com/setlists/19860300a.asp',
    ('04/00/86', '** UNKNOWN **, Atlanta, GA'): 'http://everydaycompanion.com/setlists/19860400a.asp',
    ('07/00/86', 'Washington Park, Macon, GA'): 'http://everydaycompanion.com/setlists/19860700a.asp',
    ('01/00/87', '40 Watt Club, Athens, GA'): 'http://everydaycompanion.com/setlists/19870100a.asp',
    ('10/00/87', 'Uptown Lounge, Athens, GA'): 'http://everydaycompanion.com/setlists/19871000a.asp',
    ('00/00/87', '** UNKNOWN **, ** UNKNOWN **, UU'): 'http://everydaycompanion.com/setlists/19870000a.asp',
    ('09/00/88', 'Phi Kappa Phi House, Presbyterian College, Clinton, SC'): 'NODATA',
    ('09/00/88', "O'Neilly's Pub, Macon, GA"): 'http://everydaycompanion.com/setlists/19880900a.asp',
    ('00/00/89', "W.C. Don's, Jackson, MS"): 'http://everydaycompanion.com/setlists/19890000a.asp',
    ('01/00/89', 'Phi Delta Theta House, University of Georgia, Athens, GA'): 'http://everydaycompanion.com/setlists/19890100a.asp',
    ('04/00/89', 'Sigma Alpha Epsilon House, Tuscaloosa, AL'): 'http://everydaycompanion.com/setlists/19890400b.asp',
    ('05/00/89', 'The Brewery, Raleigh, NC'): 'http://everydaycompanion.com/setlists/19890500a.asp',
    ('09/00/89', "Edgar's Campus Bar, Clemson University, Clemson, SC"): 'http://everydaycompanion.com/setlists/19890900a.asp',
    ('10/00/89', 'Elmo House, Charlottesville, VA'): 'http://everydaycompanion.com/setlists/19891000a.asp',
    ('00/00/90', "Johnny D's, Somerville, MA"): 'http://everydaycompanion.com/setlists/19900000a.asp',
    ('08/00/90', 'Excelsior Mill, Atlanta, GA'): 'http://everydaycompanion.com/setlists/19900800a.asp',
    ('00/00/91', 'Hollins University, Roanoke, VA'): 'NODATA',
    ('03/21/87', 'The Rookery, Macon, GA'): 'NODATA',
    ('02/15/24', 'Chicago Theatre, Chicago, IL'): 'NODATA',
    ('02/16/24', 'Chicago Theatre, Chicago, IL'): 'NODATA',
    ('02/17/24', 'Chicago Theatre, Chicago, IL'): 'NODATA',
}

# %%
# Multiple Shows in One Day (change Link To 'b')
multiple_shows = {
    ('07/21/91', 'Sheridan Opera House, Telluride, CO'): 'http://everydaycompanion.com/setlists/19910721b.asp',
    ('08/20/91', "Toad's Place, New Haven, CT"): 'http://everydaycompanion.com/setlists/19910820b.asp',
    ('09/21/92', "Woodsmen of the World Hall, Eugene, OR"): 'http://everydaycompanion.com/setlists/19920921b.asp',
    ('02/23/93', "Newport Music Hall, Columbus, OH"): 'http://everydaycompanion.com/setlists/19930223b.asp',
    ('05/03/93', "First Avenue, Minneapolis, MN"): 'http://everydaycompanion.com/setlists/19930503b.asp',
    ('05/12/93', "Horizontal Boogie Bar, Rochester, NY"): 'http://everydaycompanion.com/setlists/19930512b.asp',
    ('05/15/93', "Avalon, Boston, MA"): 'http://everydaycompanion.com/setlists/19930515b.asp',
    ('03/15/94', "Avalon, Boston, MA"): 'http://everydaycompanion.com/setlists/19940315b.asp',
    ('07/14/94', "The Vic Theatre, Chicago, IL"): 'http://everydaycompanion.com/setlists/19940714b.asp',
    ('11/05/94', "Arnold Hall, US Air Force Academy, Colorado Springs, CO"): 'http://everydaycompanion.com/setlists/19941105b.asp',
    ('11/06/94', "Theater, Lory Student Center, Colorado State University, Fort Collins, CO"): 'http://everydaycompanion.com/setlists/19941106b.asp',
    ('11/11/94', "Roseland Theater, Portland, OR"): 'http://everydaycompanion.com/setlists/19941111b.asp',
    ('03/25/95', "Michigan State University Auditorium, East Lansing, MI"): 'http://everydaycompanion.com/setlists/19950325b.asp',
    ('04/08/95', "Irving Plaza, New York, NY"): 'http://everydaycompanion.com/setlists/19950408b.asp',
    ('05/06/95', "Chastain Park, Atlanta, GA"): 'http://everydaycompanion.com/setlists/19950506b.asp',
    ('07/14/95', "Cain's Main Street Stage, Tulsa, OK"): 'http://everydaycompanion.com/setlists/19950714b.asp',
    ('07/18/95', "Alberta Bair Theater, Billings, MT"): 'http://everydaycompanion.com/setlists/19950718b.asp',
    ('07/22/95', "Roseland Theater, Portland, OR"): 'http://everydaycompanion.com/setlists/19950722b.asp',
    ('07/29/95', "Snow King Center, Jackson, WY"): 'http://everydaycompanion.com/setlists/19950729b.asp',
    ('04/12/97', "Backyard, Bee Cave, TX"): 'http://everydaycompanion.com/setlists/19970412b.asp',
    ('09/16/97', "Virginia Theater, Champaign, IL"): 'http://everydaycompanion.com/setlists/19970916b.asp',
    ('09/17/97', "Shryock Auditorium, Southern Illinois University, Carbondale, IL"): 'http://everydaycompanion.com/setlists/19970917b.asp',
    ('03/19/98', "Chesterfield Café, Paris, FR"): 'http://everydaycompanion.com/setlists/19980319b.asp',
    ('07/01/99', "House of Blues, West Hollywood, CA"): 'http://everydaycompanion.com/setlists/19990701b.asp',
    ('09/30/99', "Backyard, Bee Cave, TX"): 'http://everydaycompanion.com/setlists/19990930b.asp',
    ('11/17/99', "Orpheum Theater, Boston, MA"): 'http://everydaycompanion.com/setlists/19991117b.asp',
    ('07/30/00', "Alpine Stage, Bolton Valley Resort, Bolton, VT"): 'http://everydaycompanion.com/setlists/20000730b.asp',
    ('07/21/01', "Harbor Center, Portsmouth, VA"): 'http://everydaycompanion.com/setlists/20010721b.asp',
    ('10/16/01', "Paramount Theater, Seattle, WA"): 'http://everydaycompanion.com/setlists/20011016b.asp',
    ('10/24/01', "KGSR 107.1FM Studios, Austin, TX"): 'http://everydaycompanion.com/setlists/20011024b.asp',
    ('10/24/01', "Frank Erwin Center, Austin, TX"): 'http://everydaycompanion.com/setlists/20011024c.asp',
    ('11/01/01', "Roy Wilkins Civic Auditorium, St. Paul, MN"): 'http://everydaycompanion.com/setlists/20011101b.asp',
    ('11/08/01', "Orpheum Theater, Boston, MA"): 'http://everydaycompanion.com/setlists/20011108b.asp',
    ('04/11/03', "UIC Pavilion, Chicago, IL"): 'http://everydaycompanion.com/setlists/20030411b.asp',
    ('07/16/03', "Harbor Center, Portsmouth, VA"): 'http://everydaycompanion.com/setlists/20030716b.asp',
    ('07/22/03', "Paolo Soleri, Santa Fe, NM"): 'http://everydaycompanion.com/setlists/20030722b.asp',
    ('10/03/03', "Backyard, Bee Cave, TX"): 'http://everydaycompanion.com/setlists/20031003b.asp',
    ('04/08/05', "Chicago Theatre, Chicago, IL"): 'http://everydaycompanion.com/setlists/20050408b.asp',
    ('04/14/05', "Radio City Music Hall, New York, NY"): 'http://everydaycompanion.com/setlists/20050414b.asp',
    ('08/01/06', "The Palace Theatre, Louisville, KY"): 'http://everydaycompanion.com/setlists/20060801b.asp',
    ('11/02/06', "Backyard, Bee Cave, TX"): 'http://everydaycompanion.com/setlists/20061102b.asp',
    ('04/29/10', "Howlin' Wolf, New Orleans, LA"): 'http://everydaycompanion.com/setlists/20100429b.asp',
    ('06/24/10', "Twist and Shout Records, Denver, CO"): 'http://everydaycompanion.com/setlists/20100624b.asp',
    ('07/26/10', "Tennessee Theater, Knoxville, TN"): 'http://everydaycompanion.com/setlists/20100726b.asp',
    ('10/04/10', "Ryman Auditorium, Nashville, TN"): 'http://everydaycompanion.com/setlists/20101004b.asp',
    ('04/17/13', "Palace Theater, Louisville, KY"): 'http://everydaycompanion.com/setlists/20130417b.asp',
    ('01/25/19', "Hard Rock Hotel and Casino, Riviera Maya, MX"): 'http://everydaycompanion.com/setlists/20190125b.asp',
}

# %%
venue_corrections = {
    ('ADAMS CENTER', 'MT'): 'ADAMS FIELDHOUSE, UNIVERSITY OF MONTANA',
    ('AUDITORIUM THEATRE', 'CHICAGO'): 'AUDITORIUM THEATER, ROOSEVELT UNIVERSITY',
    ('BAYFRONT ARENA', 'FL'): 'BAYFRONT AUDITORIUM',
    ('FLEET PAVILION', 'BOSTON'): "CAESAR'S TAHOE",
    ("CAESAR'S TAHOE SHOWROOM", 'NV'): "CAESAR'S TAHOE"
}

# %%
city_corrections = {
    '23 EAST CABARET': 'PHILADELPHIA',
    "CAESAR'S TAHOE": 'LAKE TAHOE',
    'CYNTHIA WOODS MITCHELL PAVILLION': 'THE WOODLANDS',
    'N. LITTLE ROCK': 'LITTLE ROCK',
    'NORTH LITTLE ROCK': 'LITTLE ROCK',
    'MT. CRESTED BUTTE': 'CRESTED BUTTE',
    'SNOWMASS VILLAGE': 'SNOWMASS',
    'ELON COLLEGE': 'ELON',
    'N. MYRTLE BEACH': 'MYRTLE BEACH'
}

# %% [markdown]
# # Functions

# %%
def format_date_for_link(date_str):
    try:
        dt = datetime.strptime(date_str, "%m/%d/%y")
        return dt.strftime("%Y%m%d")
    except ValueError:
        # Handle special cases like "00/00/85"
        if date_str.startswith("00/00/"):
            return date_str[-2:] + "0000"
        elif date_str.startswith("00/"):
            month = date_str[3:5]
            year = date_str[-2:]
            return f"19{year}{month}00"
        return date_str.replace("/", "")

# %%
def update_link(row):
    key = (row['date'], row['venue'])
    if key in all_special_cases:
        return all_special_cases[key]
    return row['link']

# %%
def is_radio_show(venue, radio_terms):
    """Identify if a venue is a radio show"""
    if re.search(r'\b\d+\.\d+FM\b', venue):
        return 1
    if re.search(r'\b\d+\.\d\b', venue):
        return 1
    if any(term in venue for term in radio_terms):
        return 1
    return 0

# %%
def correct_venue_name(row, venue_corrections):
    """Apply corrections to venue names"""
    key = (row['venue_name'], row['state'])
    if key in venue_corrections:
        return venue_corrections[key]
    key2 = (row['venue_name'], row['city'])
    if key2 in venue_corrections:
        return venue_corrections[key2]
    return row['venue_name']

# %%
def correct_city(row, city_corrections):
    """Apply corrections to city names"""
    if row['venue_name'] in city_corrections:
        return city_corrections[row['venue_name']]
    if row['city'] in city_corrections:
        return city_corrections[row['city']]
    return row['city']

# %%
def process_dim(st_yr=1986, end_yr=2024):
    base_url = 'http://everydaycompanion.com/'
    tour_list = list(range(st_yr, end_yr + 1))
    tour_list = [year for year in tour_list if year != 2004]  # :(
    tour_df_list = []
    
    for year in tour_list:
        yr = str(year)[-2:]
        year_link = f"{base_url}asp/tour{yr}.asp"
        print(year_link)
        
        response = requests.get(year_link)
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='latin1')
        tour_string = soup.find('p').get_text(strip=True)
        tour_string = tour_string.replace("??", "00")
        
        # Split the string into individual dates
        venues = re.split(r'\d{2}/\d{2}/\d{2}\?*', tour_string)
        venues = [venue.strip() for venue in venues if venue.strip() != ""]
        dates = re.findall(r'\d{2}/\d{2}/\d{2}\b\?*', tour_string)
        
        tour_data = pd.DataFrame({
            'date': dates,
            'venue': venues
        })
        
        # Create links to setlists
        tour_data['link'] = tour_data['date'].apply(
            lambda x: f"{base_url}setlists/{format_date_for_link(x)}a.asp"
        )
        
        # Combine all special cases
        all_special_cases = {**SPECIAL_CASE_LINKS, **MULTIPLE_SHOWS_LINKS}
        
        # Apply special case links
        tour_data['link'] = tour_data.apply(
            lambda row: update_link(row, all_special_cases), 
            axis=1
        )
        
        # Filter out NODATA entries and get unique rows
        tour_data = tour_data[tour_data['link'] != 'NODATA'].drop_duplicates()
        
        # Extract date components from link
        tour_data['date_num'] = tour_data['link'].str.extract(r'(\d+)')
        tour_data['year'] = tour_data['date_num'].str[:4].astype(int)
        tour_data['month'] = tour_data['date_num'].str[4:6].astype(int)
        tour_data['day'] = tour_data['date_num'].str[6:8].astype(int)
        
        # Convert to proper date format
        tour_data['date'] = pd.to_datetime(
            tour_data.apply(
                lambda x: f"{x['month']:02d}/{x['day']:02d}/{x['year']:04d}", 
                axis=1
            ), 
            format="%m/%d/%Y"
        )
        
        # Process venue information
        venue_info = tour_data.apply(process_venue, axis=1)
        tour_data = pd.concat([tour_data, venue_info], axis=1)
        
        # Convert to uppercase
        tour_data['city'] = tour_data['city'].str.upper()
        tour_data['venue_name'] = tour_data['venue_name'].str.upper()
        tour_data['venue_full'] = tour_data['venue_full'].str.upper()
        
        # Add year_index
        tour_data = tour_data.reset_index(drop=True)
        tour_data['year_index'] = tour_data.index + 1
        
        # Identify radio shows
        tour_data['is_radio'] = tour_data['venue_full'].apply(
            lambda x: is_radio_show(x, RADIO_TERMS)
        )
        
        # Fix venue names
        tour_data['venue_name'] = tour_data.apply(
            lambda row: correct_venue_name(row, VENUE_CORRECTIONS), 
            axis=1
        )
        
        # Fix city names
        tour_data['city'] = tour_data.apply(
            lambda row: correct_city(row, CITY_CORRECTIONS), 
            axis=1
        )
        
        # Append to list
        tour_df_list.append(tour_data)
    
    # Combine DataFrames from loop list
    combined_df = pd.concat(tour_df_list, ignore_index=True)
    combined_df = combined_df.sort_values(['year', 'month', 'day']).reset_index(drop=True)
    combined_df['show_index'] = combined_df.index + 1
    
    # Create Run Index + Show In Run Index
    combined_df = combined_df.sort_values(['date', 'venue_name'])
    
    # Create groups based on consecutive dates and venue
    combined_df['date_diff'] = combined_df['date'].diff().dt.days != 1
    combined_df['venue_change'] = combined_df['venue_name'] != combined_df['venue_name'].shift()
    combined_df['run_break'] = combined_df['date_diff'] | combined_df['venue_change']
    combined_df['run_index'] = combined_df['run_break'].cumsum()
    
    # Calculate show_in_run
    combined_df = combined_df.sort_values(['date', 'run_index'])
    
    # Group by run_index and calculate show_in_run
    run_groups = combined_df.groupby('run_index')
    combined_df['min_show_index'] = run_groups['show_index'].transform('min')
    combined_df['show_in_run'] = combined_df['show_index'] - combined_df['min_show_index'] + 1
    
    # Select and order final columns
    result_df = combined_df[[
        'link', 'date', 'date_num', 'year', 'month', 'day', 
        'state', 'city', 'venue_name', 'venue_full', 
        'run_index', 'show_index', 'show_in_run', 'year_index', 
        'venue', 'is_radio'
    ]]
    
    return result_df

# %%
def determine_set(row):
    text = row[:3]
    if text == "??":
        return 'Details'
    elif text == "0: ":
        return '0'
    elif text == "1: ":
        return '1'
    elif text == "2: ":
        return '2'
    elif text == "3: ":
        return '3'
    elif text == "4: ":
        return '4'
    elif text == "E: ":
        return 'E'
    elif text == "E1:":
        return 'E'
    elif text == "E2:":
        return 'E'
    elif text == "E3:":
        return 'E'
    elif re.match(r"^\d{2}/", text):
        return "Details"
    elif row.startswith("*"):
        return "Song_Notes"
    elif row.startswith("["):
        return "Show_Notes"
    else:
        return "Other"

# %%
def clean_raw(row):
    if row['set'] in ['0', '1', '2', '3', '4', 'E']:
        return row['Raw'][3:]
    elif row['set'] == 'Other':
        return "* " + re.sub(r".*\*", "", row['Raw'])
    else:
        return row['Raw']

# %%
def clean_song_name(name):
    if name in ['???', 'ARU/WSP JAM']:
        return 'JAM'
    elif name == 'THIS MUST BE THE PLACE (NA<EF>VE MELODY)':
        return 'THIS MUST BE THE PLACE (NAIEVE MELODY)'
    elif name == 'W<CR>M':
        return 'WURM'
    elif name in ['LAWYERS', 'GUNS', 'AND MONEY']:
        return 'LAWYERS GUNS AND MONEY'
    else:
        return name

# %%
def process_setlist(setlist_link):
    """
    Process a setlist from everydaycompanion.com and extract song information.
    
    Args:
        setlist_link (str): URL to the setlist page
        
    Returns:
        pandas.DataFrame: Processed songs dataframe with set, song name, and notes
    """
    setlist_link = setlist_link.lower()
    
    # Fetch and parse the HTML
    response = requests.get(setlist_link)
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding='latin1')
    
    # Extract tables from the HTML
    tables = soup.find_all('table')
    if len(tables) < 6:
        print(f"Warning: Expected at least 6 tables, found {len(tables)} in {setlist_link}")
        return pd.DataFrame()
    
    # Extract the setlist table (6th table)
    setlist_table = tables[5]
    rows = setlist_table.find_all('tr')
    
    # Extract text from each row
    setlist_data = []
    for row in rows:
        cells = row.find_all('td')
        if cells:
            setlist_data.append(cells[0].get_text(strip=True))
    
    # Create DataFrame
    setlist_raw = pd.DataFrame({'X1': setlist_data})
    
    # Clean and process the data
    setlist_raw['X1'] = setlist_raw['X1'].str.replace('ï', 'i')
    
    # Determine the set for each row
    setlist_raw['set'] = setlist_raw['X1'].apply(lambda x: determine_set(x))
    setlist_raw = setlist_raw.rename(columns={"X1": "Raw"})
    
    # Clean the Raw column
    setlist_raw['Raw'] = setlist_raw.apply(clean_raw, axis=1)
    
    # Create Songs DataFrame
    songs = setlist_raw[~setlist_raw['set'].isin(['Details', 'Song_Notes', 'Show_Notes', 'Other'])].copy()
    
    # Process songs
    song_rows = []
    for _, row in songs.iterrows():
        # Split by comma
        for song_group in row['Raw'].split(','):
            # Check for segues (">")
            has_segue = " > " in song_group
            into = 1 if has_segue else 0
            
            # Split by segue
            for song in song_group.split(" > "):
                song_name = song.strip().upper()
                notes_id = song_name.count("*")
                song_notes_key = "*" * notes_id if notes_id > 0 else ""
                
                song_rows.append({
                    'link': setlist_link,
                    'set': row['set'],
                    'song_name': re.sub(r"\*", "", song_name),
                    'into': into,
                    'song_notes_key': song_notes_key,
                    'notes_id': notes_id
                })
    
    songs_df = pd.DataFrame(song_rows)
    
    # Clean song names   
    songs_df['song_name'] = songs_df['song_name'].apply(clean_song_name)
    
    # Remove duplicates and add song_index
    songs_df = songs_df.drop_duplicates()
    songs_df['song_index'] = range(1, len(songs_df) + 1)
    
    # Extract raw notes
    raw_notes = setlist_raw[setlist_raw['set'].isin(["Song_Notes", "Show_Notes", "Other"])].copy()
    
    # Process "Other" category notes
    if "Other" in setlist_raw['set'].values:
        other_rows = []
        for _, row in raw_notes[raw_notes['set'] == 'Other'].iterrows():
            for line in row['Raw'].split('\r\n'):
                line = line.strip()
                if line:
                    if line.startswith("*"):
                        set_type = "Song_Notes"
                    elif line.startswith("["):
                        set_type = "Show_Notes"
                    else:
                        set_type = "Other"
                    
                    if set_type != "Other":
                        other_rows.append({'Raw': line, 'set': set_type})
        
        other_df = pd.DataFrame(other_rows)
        raw_notes = pd.concat([raw_notes[raw_notes['set'] != 'Other'], other_df], ignore_index=True)
    
    # Create Show Notes DataFrame
    if "Show_Notes" in raw_notes['set'].values:
        show_notes = raw_notes[raw_notes['set'] == "Show_Notes"]['Raw'].tolist()
        show_notes_df = pd.DataFrame({
            'link': [setlist_link],
            'show_notes': [" ".join(show_notes)]
        })
    else:
        show_notes_df = pd.DataFrame({
            'link': [setlist_link],
            'show_notes': [""]
        })
    
    # Create Notes DataFrame
    if "Song_Notes" in raw_notes['set'].values:
        notes_str = " ".join(raw_notes[raw_notes['set'] == 'Song_Notes']['Raw'].tolist())
        
        # Split notes by asterisk pattern
        notes_split = re.split(r'(?<=[A-Za-z])\*', notes_str)
        
        for i in range(len(notes_split)):
            if i > 0:
                notes_split[i] = "*" + notes_split[i]
        
        notes_rows = []
        for note in notes_split:
            if note.strip():
                parts = note.strip().split(" ", 1)
                if len(parts) == 2:
                    notes_rows.append({
                        'link': setlist_link,
                        'song_notes_key': parts[0].strip(),
                        'song_note_detail': parts[1].strip().upper()
                    })
                else:
                    notes_rows.append({
                        'link': setlist_link,
                        'song_notes_key': parts[0].strip(),
                        'song_note_detail': ""
                    })
        
        notes_df = pd.DataFrame(notes_rows)
    else:
        notes_df = pd.DataFrame({
            'link': [setlist_link],
            'song_notes_key': [None],
            'song_note_detail': [""]
        })
    
    # Join Notes To Songs
    songs_df = songs_df.merge(show_notes_df, on='link', how='left')
    songs_df = songs_df.merge(notes_df, on=['link', 'song_notes_key'], how='left')
    
    # Select final columns
    songs_df = songs_df.drop(columns=['song_notes_key', 'notes_id'])
    
    print(f"Now Loading {setlist_link}")
    
    return songs_df

# %%
def is_radio_show(venue_full):
    if pd.isna(venue_full):
        return 0
    if re.search(r'\b\d+\.\d+FM\b', venue_full):
        return 1
    if re.search(r'\b\d+\.\d\b', venue_full):
        return 1
    if any(term in venue_full for term in [
        'NBC STUDIOS', 'ED SULLIVAN THEATER', 
        'STUDIO 6B, ROCKAFELLER CENTER', 'CNN STUDIOS',
        ' STUDIO', ' RECORD'
    ]):
        return 1
    return 0

# %%
def is_soundcheck(notes):
    if pd.isna(notes):
        return 0
    return 1 if '[Soundcheck; ' in notes else 0

# %%
def is_opening_act(notes):
    if pd.isna(notes):
        return 0
    return 1 if 'opened for' in str(notes).lower() else 0

# %%
def load_all_data(start=1986, end=2025, max_workers=4):
    """
    Load all Widespread Panic show information from EveryDayCompanion
    
    Args:
        start (int): Start year
        end (int): End year
        max_workers (int): Maximum number of parallel workers for fetching setlists
        
    Returns:
        tuple: (songs DataFrame, historical shows DataFrame, future shows DataFrame)
    """
    # Load Dim Stage 1
    print(f"Loading tour data from {start} to {end}...")
    tour_data = process_dim(st_yr=start, end_yr=end)
    
    # Split Historical and Future
    today = datetime.datetime.now().date()
    show_dim = tour_data[(tour_data['date'].dt.date < today) & 
                         (tour_data['year'] >= start) & 
                         (tour_data['year'] <= end)]
    fut_dim = tour_data[tour_data['date'].dt.date >= today]
    
    # Peek
    print(f"{len(show_dim)} Historical & {len(fut_dim)} Future Shows And EDC Links Loaded - Now Loading Setlists")
    print(show_dim.sort_values('show_index', ascending=False).head())
    
    # Load Setlists
    start_time = time.time()
    
    # Use ThreadPoolExecutor for parallel processing
    songs_list = []
    links = show_dim['link'].tolist()
    
    # Process setlists in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create a dictionary of futures to links
        future_to_link = {executor.submit(process_setlist, link): link for link in links}
        
        # Process as they complete
        for future in tqdm(as_completed(future_to_link), total=len(links), desc="Processing setlists"):
            link = future_to_link[future]
            try:
                result = future.result()
                if not result.empty:
                    songs_list.append(result)
            except Exception as exc:
                print(f"{link} generated an exception: {exc}")
    
    # Combine all song dataframes
    if songs_list:
        songs = pd.concat(songs_list, ignore_index=True)
    else:
        songs = pd.DataFrame()
    
    # Process Songs
    if not songs.empty:
        songs['song_note_detail'] = songs['song_note_detail'].apply(
            lambda x: np.nan if pd.isna(x) or x == "" else x
        )
        songs['show_notes'] = songs['show_notes'].apply(
            lambda x: np.nan if pd.isna(x) or x == "" else x
        )
        
        # Convert set to numeric
        songs['set_num'] = songs['set'].apply(lambda x: "99" if x == 'E' else x)
        songs['set'] = pd.to_numeric(songs['set_num'])
        
        # Handle special set numbering
        songs_grouped = songs.groupby('link')
        
        # Calculate min and max set for each show
        min_max_sets = songs_grouped.agg({'set': ['min', 'max']})
        min_max_sets.columns = ['min_set', 'max_set']
        min_max_sets = min_max_sets.reset_index()
        
        # Merge back to songs
        songs = songs.merge(min_max_sets, on='link')
        
        # Adjust set numbers
        songs['set'] = songs.apply(
            lambda row: 1 if (row['set'] == 0 and row['min_set'] == 0 and 
                              row['max_set'] in [99, 0]) else row['set'], 
            axis=1
        )
        
        # Select final columns
        songs = songs[['link', 'set', 'song_index', 'song_name', 'into', 'song_note_detail', 'show_notes']]
        
        # Create dim_songs
        dim_songs = songs.groupby(['link', 'show_notes']).agg({'song_index': 'max'}).reset_index()
        dim_songs = dim_songs.rename(columns={'song_index': 'n_songs'})
        
        # Remove show_notes from songs
        songs = songs.drop(columns=['show_notes'])
    else:
        dim_songs = pd.DataFrame(columns=['link', 'show_notes', 'n_songs'])
    
    # Process Show Information
    # Slim Future
    slim_fut = fut_dim.copy()
    slim_fut['is_soundcheck'] = 0
    slim_fut['is_opening_act'] = 0
    slim_fut['show_notes'] = ""
    slim_fut['n_songs'] = 0
    slim_fut['weekday'] = slim_fut['date'].dt.day_name()
    slim_fut['is_fut'] = 1
    slim_fut = slim_fut.sort_values('date')
    
    # Process historical shows
    dim = show_dim.merge(dim_songs, on='link', how='left')
    
    # Identify radio shows, soundchecks, and opening acts
    dim['is_radio'] = dim['venue_full'].apply(is_radio_show)
    dim['is_soundcheck'] = dim['show_notes'].apply(is_soundcheck)
    dim['is_opening_act'] = dim['show_notes'].apply(is_opening_act)
    dim['weekday'] = dim['date'].dt.day_name()
    dim['is_fut'] = 0
    
    # Fill NaN values
    dim['n_songs'] = dim['n_songs'].fillna(0)
    dim['show_notes'] = dim['show_notes'].fillna("")
    
    # Sort and combine with future shows
    dim = dim.sort_values('show_index')
    combined_dim = pd.concat([dim, slim_fut], ignore_index=True)
    
    # Calculate elapsed time
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    
    # Print summary
    print(f'Successfully Loaded {len(combined_dim[combined_dim["is_fut"] == 0]["link"].unique())} '
          f'Widespread Panic Shows ({len(songs)} Total Songs) in {elapsed_time:.2f} Minutes '
          f'From {combined_dim["year"].min()} to {combined_dim["year"].max()}')
    
    # Return as tuple
    return (
        songs,
        combined_dim[combined_dim['is_fut'] == 0],
        combined_dim[combined_dim['is_fut'] == 1]
    )

# %%
def update_all_data(max_workers=4):
    """
    Update the most recent Widespread Panic shows data
    
    Args:
        max_workers (int): Maximum number of parallel workers for fetching setlists
        
    Returns:
        tuple: (songs DataFrame, historical shows DataFrame, future shows DataFrame)
    """
    # Load Previous Data
    print("fix paths first")
    song_path = './Data/WSP_Song_FactTable_1986_to_2024.pkl'
    dim_hist_path = './Data/WSP_Dim_Show_Historical_1986_to_2024.pkl'
    dim_fut_path = './Data/WSP_Dim_Show_Future_2024_to_2024.pkl'
    
    # Check if data files exist
    if not all(os.path.exists(path) for path in [song_path, dim_hist_path, dim_fut_path]):
        print("Data files not found. Please run load_all_data first.")
        return None
    
    # Load previous data
    with open(dim_hist_path, 'rb') as f:
        prev_dim_hist = pickle.load(f)
    
    with open(dim_fut_path, 'rb') as f:
        prev_dim_fut = pickle.load(f)
    
    # Set Up Dim For Update
    last_show = prev_dim_hist['date'].max()
    tour_data = process_dim(st_yr=1986, end_yr=2025)
    
    today = datetime.datetime.now().date()
    update_dim = tour_data[(tour_data['date'].dt.date < today) & (tour_data['date'] > last_show)]
    fut_dim = tour_data[tour_data['date'].dt.date >= today]
    
    if len(update_dim) == 0:
        print("All Historical Shows Up to Date")
        with open(song_path, 'rb') as f:
            songs = pickle.load(f)
        with open(dim_hist_path, 'rb') as f:
            dim_hist = pickle.load(f)
        return (songs, dim_hist, fut_dim)
    else:
        # Peek
        print(f"Now Updating {len(update_dim)} Shows | {len(fut_dim)} Future Shows And EDC Links Loaded - Now Loading Setlists")
        print(update_dim.sort_values('show_index', ascending=False).head())
        
        # Load Setlists
        start_time = time.time()
        
        with open(song_path, 'rb') as f:
            prev_song = pickle.load(f)
        
        # Find links to load
        prev_links = set(prev_song['link'].unique())
        load_links = [link for link in update_dim[update_dim['date'] > last_show]['link'].unique() 
                     if link not in prev_links]
        
        # Process setlists in parallel
        update_songs_list = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_link = {executor.submit(process_setlist, link): link for link in load_links}
            
            for future in tqdm(as_completed(future_to_link), total=len(load_links), desc="Processing new setlists"):
                link = future_to_link[future]
                try:
                    result = future.result()
                    if not result.empty:
                        update_songs_list.append(result)
                except Exception as exc:
                    print(f"{link} generated an exception: {exc}")
        
        # Combine all new song dataframes
        if update_songs_list:
            update_songs = pd.concat(update_songs_list, ignore_index=True)
        else:
            update_songs = pd.DataFrame()
        
        # Process Songs
        if not update_songs.empty:
            # Clean up song data
            update_songs['song_note_detail'] = update_songs['song_note_detail'].apply(
                lambda x: np.nan if pd.isna(x) or x == "" else x
            )
            update_songs['show_notes'] = update_songs['show_notes'].apply(
                lambda x: np.nan if pd.isna(x) or x == "" else x
            )
            
            # Convert set to numeric
            update_songs['set_num'] = update_songs['set'].apply(lambda x: "99" if x == 'E' else x)
            update_songs['set'] = pd.to_numeric(update_songs['set_num'])
            
            # Handle special set numbering
            songs_grouped = update_songs.groupby('link')
            
            # Calculate min and max set for each show
            min_max_sets = songs_grouped.agg({'set': ['min', 'max']})
            min_max_sets.columns = ['min_set', 'max_set']
            min_max_sets = min_max_sets.reset_index()
            
            # Merge back to songs
            update_songs = update_songs.merge(min_max_sets, on='link')
            
            # Adjust set numbers
            update_songs['set'] = update_songs.apply(
                lambda row: 1 if (row['set'] == 0 and row['min_set'] == 0 and 
                                  row['max_set'] in [99, 0]) else row['set'], 
                axis=1
            )
            
            # Select final columns
            update_songs = update_songs[['link', 'set', 'song_index', 'song_name', 'into', 'song_note_detail', 'show_notes']]
            
            # Create dim_songs
            dim_songs = update_songs.groupby(['link', 'show_notes']).agg({'song_index': 'max'}).reset_index()
            dim_songs = dim_songs.rename(columns={'song_index': 'n_songs'})
            
            # Combine with previous songs
            all_songs = pd.concat([prev_song, update_songs.drop(columns=['show_notes'])], ignore_index=True)
        else:
            dim_songs = pd.DataFrame(columns=['link', 'show_notes', 'n_songs'])
            all_songs = prev_song
        
        # Process Show Information
        # Slim Future
        slim_fut = fut_dim.copy()
        slim_fut['is_soundcheck'] = 0
        slim_fut['is_opening_act'] = 0
        slim_fut['show_notes'] = ""
        slim_fut['n_songs'] = 0
        slim_fut['weekday'] = slim_fut['date'].dt.day_name()
        slim_fut['is_fut'] = 1
        slim_fut = slim_fut.sort_values('date')
        
        # Process new shows
        new_dim = update_dim.merge(dim_songs, on='link', how='left')
        
        # Identify radio shows, soundchecks, and opening acts
        def is_radio_show(venue_full):
            if pd.isna(venue_full):
                return 0
            if re.search(r'\b\d+\.\d+FM\b', venue_full):
                return 1
            if re.search(r'\b\d+\.\d\b', venue_full):
                return 1
            if any(term in venue_full for term in [
                'NBC STUDIOS', 'ED SULLIVAN THEATER', 
                'STUDIO 6B, ROCKAFELLER CENTER', 'CNN STUDIOS',
                ' STUDIO', ' RECORD'
            ]):
                return 1
            return 0
        
        def is_soundcheck(notes):
            if pd.isna(notes):
                return 0
            return 1 if '[Soundcheck; ' in notes else 0
        
        def is_opening_act(notes):
            if pd.isna(notes):
                return 0
            return 1 if 'opened for' in str(notes).lower() else 0
        
        new_dim['is_radio'] = new_dim['venue_full'].apply(is_radio_show)
        new_dim['is_soundcheck'] = new_dim['show_notes'].apply(is_soundcheck)
        new_dim['is_opening_act'] = new_dim['show_notes'].apply(is_opening_act)
        new_dim['weekday'] = new_dim['date'].dt.day_name()
        new_dim['is_fut'] = 0
        
        # Fill NaN values
        new_dim['n_songs'] = new_dim['n_songs'].fillna(0)
        new_dim['show_notes'] = new_dim['show_notes'].fillna("")
        
        # Sort and combine with previous historical and future shows
        new_dim = new_dim.sort_values('show_index')
        dim = pd.concat([prev_dim_hist, new_dim], ignore_index=True)
        
        # Split into historical and future
        historical_dim = dim[dim['is_fut'] == 0]
        future_dim = slim_fut
        
        # Calculate elapsed time
        end_time = time.time()
        elapsed_time = (end_time - start_time) / 60
        
        # Print summary
        print(f'Successfully Updated {len(new_dim["link"].unique())} '
              f'Widespread Panic Shows ({len(update_songs) if not update_songs.empty else 0} Total Songs) in {elapsed_time:.2f} Minutes '
              f'From {new_dim["date"].min()} to {new_dim["date"].max()}')
        
        # Return as tuple
        return (all_songs, historical_dim, future_dim)

# %%
def save_setlists(song_df, all_df):
    """
    Save the processed data to pickle files
    
    Args:
        song_df (DataFrame): Song fact table
        all_df (DataFrame): Combined show dimension table
    """
    # Create data directory if it doesn't exist
    Path("./Data").mkdir(parents=True, exist_ok=True)
    
    # Extract year range from links
    start_year = min(int(link[38:42]) for link in all_df['link'] if isinstance(link, str))
    end_year = max(int(link[38:42]) for link in all_df['link'] if isinstance(link, str))
    
    # Create paths
    fact_path = f'./Data/WSP_Song_FactTable_{start_year}_to_{end_year}.pkl'
    dim_hist_path = f'./Data/WSP_Dim_Show_Historical_{start_year}_to_{end_year}.pkl'
    dim_fut_path = f'./Data/WSP_Dim_Show_Future_{end_year}_to_{end_year}.pkl'
    dim_path = f'./Data/WSP_Show_Dim_Table_{start_year}_to_{end_year}.pkl'
    
    # Save data
    with open(fact_path, 'wb') as f:
        pickle.dump(song_df, f)
    
    with open(dim_path, 'wb') as f:
        pickle.dump(all_df, f)
    
    # Also save historical and future separately for update function
    historical_df = all_df[all_df['is_fut'] == 0]
    future_df = all_df[all_df['is_fut'] == 1]
    
    with open(dim_hist_path, 'wb') as f:
        pickle.dump(historical_df, f)
    
    with open(dim_fut_path, 'wb') as f:
        pickle.dump(future_df, f)
    
    # Print confirmation
    print(f"Setlist Data Saved To {fact_path}")
    print(f"Show Data Saved To {dim_path}")
    print(f"Historical Show Data Saved To {dim_hist_path}")
    print(f"Future Show Data Saved To {dim_fut_path}")

# %%
def main():
    # Choose whether to load all data or just update
    load_all = True  # Set to False to update instead
    
    if load_all:
        # Load All From Scratch
        print("Loading all data from scratch...")
        data_list = load_all_data(start=1986, end=2024)
    else:
        # Update Setlist Data
        print("Updating with recent shows...")
        data_list = update_all_data()
    
    if data_list is None:
        print("Error: Failed to load or update data")
        return
    
    # Create Tables
    # Song Fact Table
    fact_song = data_list[0]
    
    # Dim Historical Show (All Show Data Related To Historical Concerts)
    dim_historical = data_list[1]
    
    # Dim Future Show (All Show Data Related To Future Concerts)
    if len(data_list[2]) > 0:
        dim_future = data_list[2]
    else:
        # Load manual future shows if everydaycompanion not updated
        future_csv_path = "./Data/20250209_PanicFutureDim - FutureDim.csv"
        if os.path.exists(future_csv_path):
            dim_future = pd.read_csv(future_csv_path)
            dim_future['date_num'] = dim_future['date_num'].astype(str)
            dim_future['show_notes'] = dim_future['show_notes'].fillna("")
            
            # Filter to only future shows
            today = datetime.datetime.now().date()
            dim_future = dim_future[pd.to_datetime(dim_future['date']).dt.date >= today]
        else:
            print(f"Warning: {future_csv_path} not found. Using empty future shows DataFrame.")
            dim_future = pd.DataFrame()
    
    # Combine All
    dim_all = pd.concat([dim_historical, dim_future], ignore_index=True)
    
    # Save Tables
    save_setlists(fact_song, dim_all)
    
    print(f"Processed {len(fact_song)} songs across {len(dim_historical)} historical shows")
    print(f"Future shows: {len(dim_future)}")
    
    return fact_song, dim_all

# %% [markdown]
# # Run

# %%
if __name__ == "__main__":
    fact_song, dim_all = main()


