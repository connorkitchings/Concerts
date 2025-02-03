pip install numpy

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from io import StringIO
import os

today = datetime.today().strftime('%Y-%m-%d')

# Importing Song List from API
songlist_url_api = "https://elgoose.net/api/v2/songs.json?order_by=name"
songlistdata_json = requests.get(songlist_url_api).json()
song_df = pd.DataFrame(songlistdata_json['data'])
songdata_og = song_df.drop(columns=['slug','created_at','updated_at'])

# Pulling Song Data from El Goose Website
songlist_url = "https://elgoose.net/song/"
response = requests.get(songlist_url)
response.raise_for_status()  # Raise an exception for bad status codes
html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')
tables = soup.find_all('table')
if tables:
    tables_str = str(tables)  # Convert tables to string
    tables_io = StringIO(tables_str)  # Wrap in StringIO
    tables = pd.read_html(tables_io)
songdata_info = tables[1].copy()

# Combining Song List and Song Data into final data 
songdata = songdata_og.merge(songdata_info, left_on="name", right_on="Song Name", how="inner")[['id','Song Name', 'isoriginal','Original Artist', 'Debut Date','Last Played',\
                                                                                                'Times Played Live', 'Avg Show Gap']]
songdata = songdata.rename(columns={'Song Name': 'song_name', 'Original Artist': 'original_artist', 'Debut Date': 'debut_date', 'Last Played': 'last_played', \
                                    'Times Played Live': 'times_played_live', 'Avg Show Gap': 'avg_show_gap'})

# Importing Show List from API
showlist_url = "https://elgoose.net/api/v2/shows.json?order_by=showdate"
showlistdata_json = requests.get(showlist_url).json()
showlist_df = pd.DataFrame(showlistdata_json['data'])
past_df = showlist_df[showlist_df['showdate'] < today]
future_df = showlist_df[showlist_df['showdate'] >= today].sort_values('showdate').head(1)
result = pd.concat([past_df, future_df])
goose_showlist_df = result[(result['artist'] == 'Goose')].copy().reset_index(drop=True)

# Creating Venue Dataset
venuedata = goose_showlist_df[['venue_id', 'venuename', 'location', 'city', 'state', 'country']].drop_duplicates().sort_values(by=['venue_id'], ascending=True).reset_index(drop=True)

# Creating Tour Dataset
tourdata = goose_showlist_df[['tour_id', 'tourname']].drop_duplicates().sort_values(by=['tour_id'], ascending=True).reset_index(drop=True)

# Creating Show Dataset
showdata = goose_showlist_df[['show_id', 'showdate', 'showtitle', 'venue_id', 'tour_id', 'showorder'\
    ]].copy().sort_values(by=['showdate', 'showorder'], ascending=[True, True]).reset_index(names='show_number').assign(show_number= lambda x: x['show_number'] + 1).drop(columns=['showorder'])
showdata['showtitle'] = showdata['showtitle'].replace('', None)

# Pulling Setlist Data from API
setlist_url = "https://elgoose.net/api/v1/setlists.json?order_by=showdate"
setlistdata_json = requests.get(setlist_url).json()
setlist_df = pd.DataFrame(setlistdata_json['data'])

# Creating Transition Data
transition_data  = setlist_df[['transition_id', 'transition']].drop_duplicates().sort_values(by=['transition_id'], ascending=True).reset_index(drop=True)

# Creating Setlist Data
setlistdata = setlist_df[setlist_df['artist'] == "Goose"].copy().reset_index(drop=True)[['uniqueid', 'show_id', 'song_id','setnumber','position','tracktime','transition_id','isreprise','isjam',\
                                                                                         'footnote','isjamchart','jamchart_notes','soundcheck','isverified','isrecommended']]

# Saving all datasets to CSV
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()
base_dir = os.path.dirname(script_dir)
save_path = os.path.join(base_dir, "Data", "Goose")
songdata.to_csv(os.path.join(save_path, "songdata.csv"), index=False)
venuedata.to_csv(os.path.join(save_path, "venuedata.csv"), index=False)
showdata.to_csv(os.path.join(save_path, "showdata.csv"), index=False)
transition_data.to_csv(os.path.join(save_path, "transition_data.csv"), index=False)
setlistdata.to_csv(os.path.join(save_path, "setlistdata.csv"), index=False)