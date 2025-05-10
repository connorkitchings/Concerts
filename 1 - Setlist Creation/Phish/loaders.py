import os
from logger import get_logger

logger = get_logger(__name__)

from datetime import datetime
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
from call_api import make_api_request

def load_song_data(api_key):
    song_data = pd.DataFrame(make_api_request('songs', api_key)['data'])
    song_data = song_data.drop(columns=['slug', 'last_permalink', 'debut_permalink'])
    response = requests.get("https://phish.net/song")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = pd.read_html(StringIO(str(soup.find_all('table'))))
    if not tables:
        logger.error(f"Expected table not found in Phish song page.")
        return pd.DataFrame()
    website_data = tables[0].sort_values(by='Song Name').reset_index(drop=True)
    merged_data = song_data.merge(
        website_data,
        left_on="song",
        right_on="Song Name",
        how="inner"
    )
    final_columns = {
        'songid': 'song_id',
        'Song Name': 'song',
        'Original Artist': 'original_artist',
        'Debut': 'debut_date'
    }
    return merged_data[list(final_columns.keys())].rename(columns=final_columns)

def load_show_data(api_key):
    today = datetime.today().strftime('%Y-%m-%d')
    shows = pd.DataFrame(make_api_request('shows/artist/phish', api_key)['data'])
    past_shows = shows[shows['showdate'] < today]
    future_shows = shows[shows['showdate'] >= today].sort_values('showdate').head(1)
    all_shows = pd.concat([past_shows, future_shows])
    venue_data = (
        all_shows[['venueid', 'venue', 'city', 'state', 'country']]
        .drop_duplicates()
        .sort_values('venueid')
        .reset_index(drop=True)
    )
    show_data = (
        all_shows[['showid', 'showdate', 'venueid', 'tourid',
                   'exclude_from_stats', 'setlist_notes']]
        .sort_values('showdate')
        .reset_index(names='show_number')
        .assign(show_number=lambda x: x['show_number'] + 1)
    )
    show_data['tourid'] = show_data['tourid'].astype('Int64').astype(str)
    return show_data, venue_data

def load_setlist_data(api_key, data_dir):
    setlist_data = pd.DataFrame(make_api_request('setlists', api_key)['data'])
    last_updated = datetime.today().strftime('%Y-%m-%d')
    transition_data = (setlist_data[['transition', 'trans_mark']]
                       .drop_duplicates()
                       .sort_values(by=['transition']))
    setlist_columns = ['showid', 'uniqueid', 'songid', 'set', 'position',
                      'transition', 'isreprise', 'isjam', 'isjamchart',
                      'jamchart_description', 'tracktime', 'gap',
                      'is_original', 'soundcheck', 'footnote', 'exclude']
    setlist_df = setlist_data[setlist_columns].copy()
    return setlist_df, transition_data
