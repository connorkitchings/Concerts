import requests
from bs4 import BeautifulSoup
import pandas as pd
from logger import get_logger
logger = get_logger(__name__, add_console_handler=True)
from io import StringIO
import numpy as np
import re
from datetime import datetime
try:
    from export_data import save_wsp_data
except ImportError:
    pass

from WSP.config import SETLIST_TABLE_IDX
COMMA_SONGS = [
    'Guns', 'And Money', 'Let Me Follow You Down', 'Let Me Hold Your Hand',
    "Please Don't Go", 'Rattle', 'And Roll', 'Narrow Mind', 'Woman Smarter'
]
COMMA_SONGS_COMPLETER = {
    'Lawyers': 'Lawyers Guns And Money',
    'Baby': 'One of the 3 Baby Songs',
    'Shake': 'Shake, Rattle, And Roll',
    'Weak Brain': 'Weak Brain, Narrow Mind',
    'Man Smart': 'Man Smart, Woman Smarter'
}
EXPECTED_COLUMNS = [
    'song_name', 'set', 'song_index_set', 'song_index_show', 'into',
    'song_note_detail', 'link'
]

def get_setlist_from_link(link):
    try:
        response = requests.get(link)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')
        if not tables or len(tables) <= SETLIST_TABLE_IDX:
            logger.error(f"Not enough tables found for link {link}. Skipping.")
            return pd.DataFrame(columns=EXPECTED_COLUMNS)
        tables_str = str(tables)
        tables_io = StringIO(tables_str)
        tables = pd.read_html(tables_io)
        setlist_raw = tables[SETLIST_TABLE_IDX].copy()
    except Exception as e:
        logger.error(f"Error fetching/parsing setlist from {link}: {e}", exc_info=True)
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    if setlist_raw.empty or 0 not in setlist_raw.columns:
        logger.warning(f"Setlist table at {link} is empty or missing expected columns. Skipping.")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    setlist_raw['Raw'] = setlist_raw[0].astype(str).str.replace("ï", "i")
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
    songs3 = songs2[~songs2['Raw'].str.contains('|'.join(COMMA_SONGS))].copy()
    songs3['Raw'] = songs3['Raw'].map(COMMA_SONGS_COMPLETER).fillna(songs3['Raw'])
    songs3['song_name'] = songs3['Raw'].str.capitalize().str.strip()
    songs3['notes_id'] = songs3['song_name'].str.count(r"\*")
    songs3['song_notes_key'] = np.where(songs3['notes_id'] == 0, "", songs3['notes_id'].apply(lambda x: '*' * x))
    songs4 = songs3.reset_index(drop=True).copy()
    songs4['song_index_show'] = songs4.index + 1
    songs4['song_index_set'] = songs4.groupby('set').cumcount() + 1
    songs = songs4[['set','song_name','into','song_index_show','song_index_set','song_notes_key','notes_id']].copy()
    songs['link'] = str(link)

    songs['song_name'] = songs['song_name'].str.upper().str.replace('*', '', regex=False)
    conditions = [songs['song_name'].isin(['???', 'ARU/WSP JAM']),songs['song_name'] == 'THIS MUST BE THE PLACE (NA<EF>VE MELODY)',songs['song_name'] == 'W<CR>M']
    replacements = ['JAM','THIS MUST BE THE PLACE (NAIEVE MELODY)','WURM']
    songs['song_name'] = np.select(conditions, replacements, default=songs['song_name'])

    songs = songs[['song_name', 'set','song_index_set','song_index_show','into','song_notes_key',
                  'notes_id', 'link']]

    is_notes = songs['notes_id'].sum()
    if is_notes > 0:
        try:
            notes_df = setlist_raw.loc[setlist_raw['set'].isin(['Notes'])].loc[:, ['Raw']]
            if len(notes_df) < 2:
                logger.warning(f"Notes DataFrame too short for link {link}. Skipping notes parsing.")
                songs_final = songs.copy()
                songs_final['song_note_detail'] = ''
            else:
                notes_str_series = notes_df['Raw'].iloc[1]
                notes_split = re.split(r'(\*+|\[)', notes_str_series)
                notes_split = [s for s in notes_split if s]
                notes_split = [s for s in notes_split if s.startswith(' ') or s.startswith('*')]
                notes_df = pd.DataFrame({'song_notes_key': notes_split[::2], 'song_note_detail': notes_split[1::2]})
                if link=="http://everydaycompanion.com/setlists/20091017a.asp":
                    notes_df = pd.DataFrame({'song_notes_key':['*'], 'song_note_detail':['with The Allman Brothers']})
                if link=="http://everydaycompanion.com/setlists/20161030a.asp":
                    notes_df = pd.DataFrame({'song_notes_key':['*'], 'song_note_detail':['Steve Lopez on Percussion']})
                    notes_df['song_note_detail'] = notes_df['song_note_detail'].str.lstrip()
                songs_final = pd.merge(songs, notes_df, how='left', left_on='song_notes_key', right_on='song_notes_key')
                songs_final.drop(columns=['song_notes_key', 'notes_id'], inplace=True)
        except Exception as e:
            logger.warning(f"Error parsing notes for link {link}: {e}")
            songs_final = songs.copy()
            songs_final['song_note_detail'] = ''
    else:
        songs_final = songs.copy()
        songs_final['song_note_detail'] = ''
    songs_final = songs_final[EXPECTED_COLUMNS]
    return songs_final

def load_setlist_data(link_list: list, method: str = 'all', existing_setlist_data: 'pd.DataFrame' = None) -> 'pd.DataFrame':
    """
    Load setlist data for a list of show links, returning a single merged DataFrame.

    Args:
        link_list (list): List of show links to scrape setlists for.
        method (str): Scraping method ('all', 'update', etc.). Defaults to 'all'.
        existing_setlist_data (pd.DataFrame, optional): Existing setlist data to update. Defaults to None.
    Returns:
        pd.DataFrame: Merged DataFrame of setlist data.
    """
    if existing_setlist_data is not None:
        logger.info(f"Loaded existing setlistdata.csv with {len(existing_setlist_data):,} rows.")
    else:
        logger.info("No existing setlistdata.csv found.")
    if method == 'all':
        logger.info("Loading All WSP Setlist Data")
        setlist_frames = []
        for link in link_list:
            setlist = get_setlist_from_link(link)
            if setlist is not None and not setlist.empty:
                setlist_frames.append(setlist)
            else:
                match = re.search(r'(\d{8})[a-z]\.asp', link)
                if match:
                    showdate = match.group(1)
                    try:
                        formatted_date = datetime.strptime(showdate, "%Y%m%d").strftime("%m/%d/%Y")
                    except ValueError:
                        formatted_date = showdate
                    logger.warning(f"No setlist data returned for date {formatted_date}, skipping.")
                else:
                    logger.warning(f"No setlist data returned for link {link}, skipping.")
        if not setlist_frames:
            logger.error("No setlist data found for any link.")
            return pd.DataFrame(columns=EXPECTED_COLUMNS)
        all_setlists = pd.concat(setlist_frames, ignore_index=True)
        all_setlists = all_setlists.dropna(subset=['song_name']).reset_index(drop=True)
        return all_setlists
    elif method == 'update':
        logger.info("Updating Existing WSP Setlist Data")
        if existing_setlist_data is None:
            logger.error("No existing setlist data provided for update mode.")
            return pd.DataFrame(columns=EXPECTED_COLUMNS)
        filtered_link_list = [link for link in link_list if str(datetime.today().year) in link.split('/')[-1] or str(datetime.today().year - 1) in link.split('/')[-1]]
        all_setsets = existing_setlist_data.copy()
        for link in filtered_link_list:
            setlist = get_setlist_from_link(link)
            if setlist is not None and not setlist.empty:
                all_setsets = pd.concat([all_setsets, setlist])
                all_setsets = all_setsets.drop_duplicates(subset=['link', 'song_name', 'set', 'song_index_show', 'song_index_set']).reset_index(drop=True)
            else:
                match = re.search(r'(\d{8})[a-z]\.asp', link)
                if match:
                    showdate = match.group(1)
                    try:
                        formatted_date = datetime.strptime(showdate, "%Y%m%d").strftime("%m/%d/%Y")
                    except ValueError:
                        formatted_date = showdate
                    logger.warning(f"No setlist data returned for date {formatted_date}, skipping.")
                else:
                    logger.warning(f"No setlist data returned for link {link}, skipping.")
        all_setsets = all_setsets.dropna(subset=['song_name']).reset_index(drop=True)
        return all_setsets
    else:
        logger.error(f"Unknown method '{method}' for load_setlist_data.")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

