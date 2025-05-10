import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import re
from logger import get_logger

logger = get_logger(__name__)

import os
import json
from datetime import datetime
from scrape_songs import scrape_um_songs
from scrape_shows import scrape_um_shows
from save_data import save_um_data, save_query_data
from utils import get_data_dir

BASE_URL = "https://allthings.umphreys.com"

def load_existing_data(data_dir):
    """Load existing song, venue, and setlist data if available."""
    files = ['songdata.csv', 'venuedata.csv', 'setlistdata.csv']
    data = {}
    for fname in files:
        fpath = os.path.join(data_dir, fname)
        if os.path.exists(fpath):
            data[fname] = pd.read_csv(fpath)
        else:
            data[fname] = pd.DataFrame()
    return data

def get_last_update_time(data_dir):
    last_updated_path = os.path.join(data_dir, "last_updated.json")
    if os.path.exists(last_updated_path):
        with open(last_updated_path, "r") as f:
            meta = json.load(f)
            return meta.get("last_updated")
    return None

def get_setlist_from_url(url, show_date=None):
    """
    Extract setlist data from a specific URL.
    Args:
        url: URL to the setlist page.
        show_date: Date of the show (optional, for reference).
    Returns:
        DataFrame containing setlist data for the show.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')
        if not tables or len(tables) == 0:
            logger.warning(f"No tables found for setlist at {url}")
            return pd.DataFrame()
        tables_str = str(tables)
        tables_io = StringIO(tables_str)
        tables = pd.read_html(tables_io)
        song_table = tables[0].copy().sort_values(by='Date Played').reset_index(drop=True)
        if show_date is not None:
            song_table['Show Date'] = show_date
        if 'Show Gap' in song_table.columns:
            song_table = song_table.drop(columns=['Show Gap'])
        song_table['Date Played'] = pd.to_datetime(song_table['Date Played']).dt.date
        return song_table
    except Exception as e:
        logger.error(f"Error fetching setlist from {url}: {e}", exc_info=True)
        return pd.DataFrame()

def scrape_um_setlist_data(base_url=BASE_URL):
    """
    Scrape all setlist data from allthings.umphreys.com by iterating over all songs.
    Returns a DataFrame for setlist data.
    """
    songlist_url = f"{base_url}/song/"
    response = requests.get(songlist_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    if tables:
        tables_str = str(tables)
    else:
        logger.error("No tables found on UM songlist page.")
        return pd.DataFrame()
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
            logger.warning(f"No tables found for song {song} at {song_url}")
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
        logger.error("No setlists could be parsed from UM song pages.")
        return pd.DataFrame()
    setlist_data = pd.concat(setlists).reset_index(drop=True)
    setlist_data['Footnote'] = setlist_data['Footnote'].fillna('')
    setlist_data = setlist_data.sort_values(by=['Date Played', 'Song Name'], ascending=[False, True]).reset_index(drop=True)
    return setlist_data

def update_um_data():
    data_dir = get_data_dir()
    existing_data = load_existing_data(data_dir)
    last_update = get_last_update_time(data_dir)
    logger.info(f"Last update: {last_update}")

    # Update song catalog
    logger.info("Checking for new songs...")
    new_song_data = scrape_um_songs()
    if not existing_data['songdata.csv'].empty:
        merged_songs = pd.concat([existing_data['songdata.csv'], new_song_data]).drop_duplicates(subset=['Song Name'])
    else:
        merged_songs = new_song_data

    # Update venue data
    logger.info("Checking for new venues...")
    _, new_venue_data = scrape_um_shows()
    if not existing_data['venuedata.csv'].empty:
        merged_venues = pd.concat([existing_data['venuedata.csv'], new_venue_data]).drop_duplicates()
    else:
        merged_venues = new_venue_data

    # Update setlist data
    logger.info("Checking for new setlists...")
    new_setlist_data = create_um_setlist_data()
    if not existing_data['setlistdata.csv'].empty:
        merged_setlists = pd.concat([existing_data['setlistdata.csv'], new_setlist_data]).drop_duplicates()
    else:
        merged_setlists = new_setlist_data

    logger.info("Saving updated data...")
    save_um_data(merged_songs, merged_venues, merged_setlists, data_dir)
    save_query_data(data_dir)
    logger.info("UM data update complete.")
