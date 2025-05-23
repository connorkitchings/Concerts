import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
from logger import get_logger
from utils import get_data_dir

logger = get_logger(__name__)

def fetch_setlist_urls():
    year_list = list(range(1998, datetime.now().year + 1)) # for full setlist creation
    #year_list = [datetime.now().year - 2, datetime.now().year - 1, datetime.now().year] # for update version
    url_list = []
    for year in year_list:
        urls = fetch_setlist_urls_by_year(year)
        url_list.extend(urls)
    logger.info(f"{len(url_list):,} total shows found.")
    return url_list

def fetch_setlist_urls_by_year(year):
    url = f"https://allthings.umphreys.com/setlists/{year}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Regex pattern for dates like "January 22, 2000"
    #date_pattern = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, 2000$")
    date_pattern = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}$")

    # Base URL to prepend
    base_url = "https://allthings.umphreys.com"

    # Extract (date, url) pairs
    date_url_pairs = []
    for a in soup.find_all("a", href=True):
        link_text = a.get_text(strip=True)
        if date_pattern.match(link_text):
            full_url = base_url + a['href']
            date_url_pairs.append({
            "date": link_text,
            "url": full_url
        })
    url_list = [x['url'] for x in date_url_pairs]
    logger.info(f"Found {len(url_list):,} setlists for {year}.")
    return url_list

def parse_setlist_link(link):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract metadata from the header
        header = soup.find("div", class_="setlist-date-long")
        if not header:
            logger.warning(f"Missing header for setlist page: {link}")
            return pd.DataFrame(columns=["song", "set", "set_index", "show_index", "date", "venue", "city", "state", "country", "link", "footnotes"])
        a_tags = header.find_all("a")
        def safe_get(idx):
            return a_tags[idx].text.strip() if len(a_tags) > idx else None
        date = safe_get(1)
        venue = safe_get(3)
        city = safe_get(4)
        state = safe_get(5)
        country = safe_get(6)
        # Log if any are missing
        missing = []
        for field, val in zip(["date", "venue", "city", "state", "country"], [date, venue, city, state, country]):
            if val is None:
                missing.append(field)
        if missing:
            # Prefer date for log context, fallback to link
            log_id = date if date else link
            logger.info(f"Missing fields ({', '.join(missing)}) for setlist: {log_id}")
        # Adjustment for missing country
        if not country:
            log_id = date if date else link
            # If city or state has a comma, split and shift only the right part
            if city and ',' in city:
                logger.info(f"Splitting city field on comma and shifting right for setlist page: {log_id}")
                city_left, city_right = [s.strip() for s in city.split(',', 1)]
                # Shift: country <- state, state <- city_right, city <- city_left
                country = state
                state = city_right
                city = city_left
            elif state and ',' in state:
                logger.info(f"Splitting state field on comma and shifting right for setlist page: {log_id}")
                state_left, state_right = [s.strip() for s in state.split(',', 1)]
                country = state_right
                state = state_left
            else:
                # Move state to country, clear state
                logger.info(f"Moving state to country for setlist page: {log_id}")
                country = state
                state = None
        # If all are missing, skip
        if all(x is None for x in [date, venue, city, state, country]):
            logger.warning(f"All location fields missing for setlist page: {link}")
            return pd.DataFrame(columns=["song", "set", "set_index", "show_index", "footnotes","date", "venue", "city", "state", "country", "link"])

        # ... rest of function ...
    except Exception as e:
        logger.error(f"Error parsing setlist page {link}: {e}")
        return pd.DataFrame(columns=["song", "set", "set_index", "show_index", "date", "venue", "city", "state", "country", "link", "footnotes"])

    # --- Footnote extraction ---
    footnotes_map = {}
    footnotes_section = soup.select_one(".setlist-footnotes")
    if footnotes_section:
        for line in footnotes_section.stripped_strings:
            if line.startswith("[") and "]" in line:
                key = line.split("]")[0].strip("[]")
                value = line.split("]")[1].strip()
                footnotes_map[key] = value
    # --- End footnote extraction ---

    # Initialize results
    records = []
    encore_count = 0
    show_index = 0

    # Locate the body with sets
    setlist_body = soup.find("div", class_="setlist-body")
    paragraphs = setlist_body.find_all("p")

    for p in paragraphs:
        b_tag = p.find("b")
        if not b_tag:
            continue

        set_label = b_tag.text.replace(":", "").strip()
        # Handle 'One Set' as set '1'
        if set_label.lower() == "one set":
            set_name = "1"
        elif set_label.lower().startswith("set"):
            set_number = set_label.lower().replace("set", "").strip()
            set_name = set_number
        elif "encore" in set_label.lower():
            encore_count += 1
            set_name = "E" if encore_count == 1 else f"E{encore_count}"
        else:
            continue

        songs = p.find_all("span", class_="setlist-songbox")
        for set_index, song_span in enumerate(songs, start=1):
            # Extract song name and footnote key (superscript)
            song_name = song_span.get_text(strip=True).split("[")[0].strip(",> ")
            sup = song_span.find("sup")
            footnote_key = sup.text.strip("[]") if sup else ""
            show_index += 1
            records.append({
                "song": song_name,
                "set": set_name,
                "in_set_index": set_index,
                "in_show_index": show_index,
                "footnotes": footnotes_map.get(footnote_key, "") if footnote_key else "",
                "date": date,
                "venue": venue,
                "city": city,
                "state": state,
                "country": country,
                "link": link
            })

    # Convert to DataFrame
    df = pd.DataFrame(records)
    # Defensive: Only convert if 'date' exists and not empty
    if not df.empty and 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['date'] = df['date'].dt.strftime('%m/%d/%Y')
    else:
        df['date'] = pd.NaT
    return df

def fetch_requested_setlists(url_list):
    all_dfs = []
    scraped_links = set()
    for i, url in enumerate(url_list, 1):
        df = parse_setlist_link(url)
        if not df.empty and not df.isna().all().all():
            all_dfs.append(df)
            scraped_links.update(df['link'].dropna().unique())
        if i % 50 == 0:
            logger.info(f"Parsed {i} setlists so far...")
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        missed_urls = [url for url in url_list if url not in scraped_links]
        if missed_urls:
            logger.warning(f"Missed {len(missed_urls):,} setlists: {missed_urls}")
        return final_df
    else:
        return pd.DataFrame(columns=["song", "set", "set_index", "show_index", "date", "venue", "city", "state", "country", "link", "footnotes"])
    

def fetch_um_setlist_data():
    url_list = fetch_setlist_urls()
    # Load existing setlist data
    data_dir = get_data_dir()
    setlist_path = os.path.join(data_dir, 'setlistdata.csv')
    if os.path.exists(setlist_path):
        existing_df = pd.read_csv(setlist_path)
        existing_urls = existing_df['link'].unique().tolist()
        logger.info(f"Found {len(existing_urls):,} existing setlists.")
        new_urls = [url for url in url_list if url not in existing_urls]
        logger.info(f"There are {len(new_urls):,} new setlists to scrape.")
        if len(new_urls) == 0:
            logger.info("No new setlists to scrape.")
            return existing_df
        new_df = fetch_requested_setlists(new_urls)
        final_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates()
    else:
        logger.info(f"No existing setlist data found, starting fresh.")
        final_df = fetch_requested_setlists(url_list)
    return final_df
    
