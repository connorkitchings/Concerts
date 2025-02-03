import requests
import json
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from io import StringIO
import os

today = datetime.today().strftime('%Y-%m-%d')

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()
base_dir = os.path.dirname(script_dir)
higher_dir = os.path.dirname(base_dir)
credentials_dir = os.path.join(higher_dir, "Credentials")
with open(os.path.join(credentials_dir, "phish_net.txt"), "r") as file:
    line = file.readline().strip()  # Read the first line and remove whitespace

# Extract the API key
api_key = line.split(": ")[1].strip("'")

# Importing Song List from API
songlist_url_api = "https://api.phish.net/v5/songs.json?order_by=song&apikey=" + api_key
songlistdata_json = requests.get(songlist_url_api).json()
song_df = pd.DataFrame(songlistdata_json['data'])
songdata_og = song_df.drop(columns=['slug','last_permalink','debut_permalink'])

# Pulling Song Data from Phish.netWebsite
songlist_url = "https://phish.net/song"
response = requests.get(songlist_url)
response.raise_for_status()  # Raise an exception for bad status codes
html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')
tables = soup.find_all('table')
if tables:
    tables_str = str(tables)  # Convert tables to string
    tables_io = StringIO(tables_str)  # Wrap in StringIO
    tables = pd.read_html(tables_io)
songdata_info = tables[0].copy().sort_values(by='Song Name').reset_index(drop=True)

# Combining Song List and Song Data into final data 
songdata = songdata_og.merge(songdata_info, left_on="song", right_on="Song Name", how="inner")[['songid','Song Name', 'Original Artist', 'Debut','last_played',\
                                                                                                'times_played', 'gap']]
songdata = songdata.rename(columns={'songid': 'song_id', 'Song Name': 'song', 'Original Artist': 'original_artist', 'Debut': 'debut_date', 
                                    'last_played': 'last_played'})

# Importing Show List from API
showlist_url = "https://api.phish.net/v5/shows/artist/phish.json?order_by=showdate&apikey=" + api_key
showlistdata_json = requests.get(showlist_url).json()
showlist_df = pd.DataFrame(showlistdata_json['data'])
past_df = showlist_df[showlist_df['showdate'] < today]
future_df = showlist_df[showlist_df['showdate'] >= today].sort_values('showdate').head(1)
phish_showlist_df = pd.concat([past_df, future_df])

# Creating Venue Dataset
venuedata = phish_showlist_df[['venueid', 'venue', 'city', 'state', 'country']].drop_duplicates().sort_values(by=['venueid'], ascending=True).reset_index(drop=True)

# Creating Tour Dataset
tourdata = phish_showlist_df[['tourid', 'tour_name']].drop_duplicates().sort_values(by=['tourid'], ascending=True).reset_index(drop=True)

# Creating Show Dataset
showdata = (phish_showlist_df[['showid', 'showdate', 'venueid', 'tourid', 'exclude_from_stats','setlist_notes']]
            .copy().sort_values(by=['showdate'], ascending=[True])
            .reset_index(names='show_number')
            .assign(show_number= lambda x: x['show_number'] + 1)
)
showdata['tourid'] = showdata['tourid'].astype('Int64').astype(str)

# Pulling Setlist Data from API
setlist_url = "https://api.phish.net/v5/setlists.json?apikey=" + api_key
setlistdata_json = requests.get(setlist_url).json()
setlist_df = pd.DataFrame(setlistdata_json['data'])

# Creating Transition Data
transition_data  = setlist_df[['transition', 'trans_mark']].drop_duplicates().sort_values(by=['transition'], ascending=True).reset_index(drop=True)

# Creating Setlist Data
setlistdata = setlist_df[['showid', 'uniqueid', 'songid','set','position','transition','isreprise','isjam','isjamchart', 'jamchart_description',
                          'tracktime', 'gap', 'is_original','soundcheck','footnote','exclude']].copy()

save_path = os.path.join(base_dir, "Data", "Phish")
songdata.to_csv(os.path.join(save_path, "songdata.csv"), index=False)
venuedata.to_csv(os.path.join(save_path, "venuedata.csv"), index=False)
showdata.to_csv(os.path.join(save_path, "showdata.csv"), index=False)
transition_data.to_csv(os.path.join(save_path, "transition_data.csv"), index=False)
setlistdata.to_csv(os.path.join(save_path, "setlistdata.csv"), index=False)
