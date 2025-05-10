import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
from logger import get_logger
from utils import get_data_dir

logger = get_logger(__name__)

BASE_URL = "https://allthings.umphreys.com/setlists/umphreys-mcgee/"


def parse_setlist(setlist_div):
    # Extract raw date text
    date_text = setlist_div.select_one(".setlist-date-long .setlist-date").get_text(separator=" ").strip()
    date_parts = date_text.split()
    raw_date = " ".join(date_parts[:3])  # Example: 'January 21, 1998'
    try:
        date = datetime.strptime(raw_date, "%B %d, %Y").strftime("%m/%d/%Y")
    except ValueError:
        date = raw_date  # fallback if date format is off

    # Extract venue
    venue_tag = setlist_div.select_one(".setlist-date-long .venue")
    venue = venue_tag.text.strip() if venue_tag else ""

    # Get footnotes
    footnotes_map = {}
    footnotes_section = setlist_div.select_one(".setlist-footnotes")
    if footnotes_section:
        for line in footnotes_section.stripped_strings:
            if line.startswith("[") and "]" in line:
                key = line.split("]")[0].strip("[]")
                value = line.split("]")[1].strip()
                footnotes_map[key] = value

    # Get songs in all sets
    result_rows = []
    set_blocks = setlist_div.select(".setlist-body p")
    for block in set_blocks:
        set_tag = block.select_one("b.setlabel")
        if not set_tag:
            continue
        set_label = set_tag.text.replace(":", "").strip()
        set_label = set_label.replace("One Set", "1").replace("Set", "").replace("3rd E", "E3").replace("2nd E", "E2").replace("Encore", "E")
        set_label = set_label.strip()
        
        song_spans = block.select(".setlist-songbox")
        song_data = []
        for span in song_spans:
            a_tag = span.find("a")
            if not a_tag:
                continue
            song_name = a_tag.text.strip()
            sup = span.find("sup")
            footnote = sup.text.strip("[]") if sup else ""
            song_data.append((song_name, footnote))
        for i, (song, note_key) in enumerate(song_data):
            result_rows.append({
                "Song Name": song,
                "Date Played": date,
                "Venue": venue,
                "Set": set_label,
                "Song Before": song_data[i - 1][0] if i > 0 else None,
                "Song After": song_data[i + 1][0] if i < len(song_data) - 1 else None,
                "Footnote": footnotes_map.get(note_key, "") if note_key else ""
            })
    return result_rows


def fetch_um_setlists_for_year(year):
    url = f"{BASE_URL}{year}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    all_rows = []
    setlists = soup.select(".setlist.setlist-container")
    for setlist_div in setlists:
        all_rows.extend(parse_setlist(setlist_div))
    return pd.DataFrame(all_rows)


def fetch_um_setlists_for_years(years):
    all_dfs = []
    for year in years:
        df = fetch_um_setlists_for_year(year)
        all_dfs.append(df)
    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    else:
        return pd.DataFrame(columns=["Song Name", "Date Played", "Venue", "Set", "Song Before", "Song After", "Footnote"])


def full_um_setlist_update():
    current_year = datetime.now().year
    years = list(range(1998, current_year + 1))
    return fetch_um_setlists_for_years(years)


def incremental_um_setlist_update():
    current_year = datetime.now().year
    years = [current_year - 1, current_year]
    # Load existing data
    data_dir = get_data_dir()
    setlist_path = os.path.join(data_dir, 'setlistdata.csv')
    if os.path.exists(setlist_path):
        existing_df = pd.read_csv(setlist_path)
    else:
        existing_df = pd.DataFrame(columns=["Song Name", "Date Played", "Venue", "Set", "Song Before", "Song After", "Footnote"])
    # Fetch new data
    new_df = fetch_um_setlists_for_years(years)
    # Append and drop duplicates
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["Song Name", "Date Played", "Venue", "Set"], keep="last")
    return combined_df

def _set_order_key(set_label):
    # Extract leading number if present, then E, then others
    if pd.isnull(set_label):
        return (99, set_label)
    s = str(set_label).strip().upper()
    # Handle sets like '1', '2', 'E', 'E2', etc.
    if s.isdigit():
        return (int(s), '')
    if s.startswith('E') and (len(s) == 1 or s[1:].isdigit()):
        # E, E2, E3, etc. (encores after numbered sets)
        return (90 + int(s[1:] or '1'), '')
    return (99, s)

def _sort_setlist_df(df):
    df = df.copy()
    # Normalize Set column
    def normalize_set(s):
        if pd.isnull(s):
            return s
        s = str(s).strip().upper()
        s = s.replace("ONE SET", "1").replace("SET", "")
        s = s.replace("3RD E", "E3").replace("2ND E", "E2").replace("ENCORE", "E")
        return s.strip()
    df['Set'] = df['Set'].apply(normalize_set)
    # Ensure date is datetime for sorting
    df['Date Played'] = pd.to_datetime(df['Date Played'], errors='coerce')
    df['__set_order'] = df['Set'].apply(_set_order_key)
    df = df.sort_values(by=['Date Played', '__set_order'], ascending=[False, True])
    df = df.drop(columns=['__set_order'])
    # Convert date back to string in mm/dd/yyyy
    df['Date Played'] = df['Date Played'].dt.strftime('%m/%d/%Y')
    return df

def save_um_setlist_data(df, data_dir):
    setlist_path = os.path.join(data_dir, 'setlistdata.csv')
    df = _sort_setlist_df(df)
    df.to_csv(setlist_path, index=False)

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
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract date
        date_tag = soup.select_one('.setlist-date-long')
        if date_tag:
            raw_date = date_tag.text.strip()
            # Split on newline or em dash (—)
            if '\n' in raw_date:
                date_str = raw_date.split('\n')[0].strip()
            elif '—' in raw_date:
                date_str = raw_date.split('—')[0].strip()
            else:
                date_str = raw_date.strip()
            # Try parsing date
            try:
                parsed_date = pd.to_datetime(date_str, errors='coerce').date()
            except Exception:
                parsed_date = date_str
        else:
            parsed_date = show_date if show_date is not None else None
        # Extract venue
        venue_tag = soup.select_one('a.venue')
        venue = venue_tag.text.strip() if venue_tag else ''
        # Extract setlist
        setlist_rows = []
        setlist_body = soup.select_one('.setlist-body')
        if setlist_body:
            for row in setlist_body.select('tr'):
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    song_name = cols[1].text.strip()
                    set_name = cols[3].text.strip() if len(cols) > 3 else ''
                    footnote = cols[-1].text.strip() if len(cols) > 4 else ''
                    setlist_rows.append({
                        'Song Name': song_name,
                        'Date Played': parsed_date,
                        'Venue': venue,
                        'Set': set_name,
                        'Footnote': footnote
                    })
        # Extract footnotes map if present (optional, as in notebook)
        # ... (leave as is or add if needed)
        if not setlist_rows:
            logger.warning(f"No setlist rows found for setlist at {url}")
            return pd.DataFrame()
        df = pd.DataFrame(setlist_rows)
        # Ensure Date Played is a date
        df['Date Played'] = pd.to_datetime(df['Date Played'], errors='coerce').dt.date
        return df
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

def update_um_setlist_data(existing_setlist_data, venue_data, base_url=BASE_URL):
    """
    Incrementally update setlist data by only fetching shows newer than the latest in existing_setlist_data.
    Args:
        existing_setlist_data: DataFrame of current setlist data (may be empty)
        venue_data: DataFrame of current venue data
        base_url: Base URL for scraping
    Returns:
        Updated DataFrame containing all setlist data
    """
    if existing_setlist_data is None or existing_setlist_data.empty:
        # No existing data, do full scrape
        logger.warning("No existing setlist data found, falling back to full scrape.")
        return scrape_um_setlist_data(base_url=base_url)
    try:
        last_show = pd.to_datetime(existing_setlist_data['Date Played'], errors='coerce').max().date()
    except Exception as e:
        logger.warning(f"Could not determine last show date from setlistdata.csv: {e}")
        return scrape_um_setlist_data(base_url=base_url)
    # Ensure 'Last Played' is datetime.date
    venue_data['Last Played'] = pd.to_datetime(venue_data['Last Played'], errors='coerce').dt.date
    # Only consider venues with a new show
    venues_with_new_shows = venue_data[(venue_data['Last Played'] > last_show)].copy().reset_index(drop=True)
    new_setlists = []
    for _, venue_row in venues_with_new_shows.iterrows():
        venue_name = venue_row['Venue Name']
        city = venue_row['City']
        state = venue_row['State']
        country = venue_row['Country']
        # Build venue URL (site uses hyphens and lowercase)
        venue_url_components = [
            str(venue_name).replace(' ', '-').lower() if pd.notna(venue_name) else '',
            str(city).replace(' ', '-').lower() if pd.notna(city) else '',
            str(state).replace(' ', '-').lower() if pd.notna(state) else '',
            str(country).replace(' ', '-').lower() if pd.notna(country) else ''
        ]
        venue_url = f"{base_url}/venues/" + '-'.join([c for c in venue_url_components if c])
        try:
            resp = requests.get(venue_url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Find all show rows (should be <a> tags with href to setlist)
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Only consider setlist links
                if '/setlists/' in href:
                    # Extract show date from link text or href
                    show_text = link.text.strip()
                    # Try to parse date from link or nearby table cell
                    date_match = re.search(r'(\w+ \d{1,2}, \d{4})', show_text)
                    if date_match:
                        show_date = pd.to_datetime(date_match.group(1), errors='coerce').date()
                    else:
                        # fallback: try to parse from href
                        href_date_match = re.search(r'(\w+-\d{1,2}-\d{4})', href)
                        if href_date_match:
                            show_date = pd.to_datetime(href_date_match.group(1).replace('-', ' '), errors='coerce').date()
                        else:
                            continue
                    if show_date and show_date > last_show:
                        setlist_url = base_url + href if href.startswith('/') else href
                        setlist_df = get_setlist_from_url(setlist_url, show_date)
                        if not setlist_df.empty:
                            new_setlists.append(setlist_df)
        except Exception as e:
            logger.error(f"Error processing venue {venue_name}: {e}")
    if new_setlists:
        new_setlists = pd.concat(new_setlists).reset_index(drop=True)
        # Only keep columns that exist in existing_setlist_data
        cols = [c for c in existing_setlist_data.columns if c in new_setlists.columns]
        new_setlists = new_setlists[cols]
        final_setlist = pd.concat([existing_setlist_data, new_setlists]).sort_values(by=['Date Played', 'Song Name'], ascending=[False, True]).reset_index(drop=True)
    else:
        final_setlist = existing_setlist_data
    final_setlist['Footnote'] = final_setlist['Footnote'].fillna('')
    return final_setlist

def update_um_data(existing_setlist_data, merged_venues, base_url=BASE_URL):
    """
    Update setlist data incrementally. Returns the updated setlist DataFrame.
    Args:
        existing_setlist_data: DataFrame of current setlist data (may be empty)
        merged_venues: DataFrame of current venue data
        base_url: Base URL for scraping
    Returns:
        Updated DataFrame containing all setlist data
    """
    logger.info("Incrementally updating setlist data...")
    merged_setlists = update_um_setlist_data(existing_setlist_data, merged_venues, base_url=base_url)
    return merged_setlists
