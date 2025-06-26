"""
Phish data loaders for API and web scraping. All config dependencies removed; paths are hardcoded.
"""

import os
from datetime import datetime
from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .call_api import make_api_request
from .utils import get_logger

# Ensure logs/Goose/ is always relative to the project root, not src/
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
logs_dir = os.path.join(project_root, "logs", "Phish")
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "phish_pipeline.log")
logger = get_logger(__name__, log_file=log_file, add_console_handler=True)
DATA_COLLECTED_DIR = os.path.join(project_root, "data", "phish", "collected")


def get_next_show_info(show_data: pd.DataFrame, api_key: str) -> dict:
    """
    Get next show info (show_date, venue_name, city, state) by calling the Goose API.
    Returns dict with these keys (values can be None if not found).
    """
    today = datetime.today().strftime("%Y-%m-%d")
    next_show_row = (
        show_data[show_data["showdate"] >= today].sort_values("showdate").head(1)
    )
    show_id = next_show_row.iloc[0]["showid"]
    result = {"show_date": None, "venue_name": None, "city": None, "state": None}
    if show_id is not None:
        try:
            api_response = make_api_request(f"shows/showid/{show_id}", api_key)["data"]
            if api_response:
                api_show = api_response
                if isinstance(api_show, list):
                    api_show = api_show[0] if api_show else None
                if isinstance(api_show, dict):
                    result["show_date"] = api_show.get("showdate") or api_show.get(
                        "show_date"
                    )
                    result["venue_name"] = api_show.get("venue")
                    result["city"] = api_show.get("city")
                    result["state"] = api_show.get("state")
        except Exception as e:
            logger.warning(
                "Failed to fetch show info from API for show_id=%s: %s", show_id, e
            )
    return result


def load_song_data(api_key: str) -> "pd.DataFrame":
    """
    Load song data from the Phish API.

    Args:
        api_key (str): API key for authentication.
    Returns:
        pd.DataFrame: DataFrame containing song data.
    """
    song_data = pd.DataFrame(make_api_request("songs", api_key)["data"])
    song_data = song_data.drop(columns=["slug", "last_permalink", "debut_permalink"])
    response = requests.get("https://phish.net/song", timeout=60)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    tables = pd.read_html(StringIO(str(soup.find_all("table"))))
    if not tables:
        logger.error("Expected table not found in Phish song page.")
        return pd.DataFrame()
    website_data = tables[0].sort_values(by="Song Name").reset_index(drop=True)
    merged_data = song_data.merge(
        website_data, left_on="song", right_on="Song Name", how="inner"
    )
    final_columns = {
        "songid": "song_id",
        "Song Name": "song",
        "Original Artist": "original_artist",
        "Debut": "debut_date",
    }
    return merged_data[list(final_columns.keys())].rename(columns=final_columns)


def load_show_data(api_key: str) -> tuple["pd.DataFrame", "pd.DataFrame"]:
    """
    Load show and venue data from the Phish API.

    Args:
        api_key (str): API key for authentication.
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Tuple of DataFrames for show data and venue data.
    """
    today = datetime.today().strftime("%Y-%m-%d")
    shows = pd.DataFrame(make_api_request("shows/artist/phish", api_key)["data"])
    past_shows = shows[shows["showdate"] < today]
    future_shows = shows[shows["showdate"] >= today].sort_values("showdate").head(1)
    all_shows = pd.concat([past_shows, future_shows])
    venue_data = (
        all_shows[["venueid", "venue", "city", "state", "country"]]
        .drop_duplicates()
        .sort_values("venueid")
        .reset_index(drop=True)
    )
    show_data = (
        all_shows[
            [
                "showid",
                "showdate",
                "venueid",
                "tourid",
                "exclude_from_stats",
                "setlist_notes",
            ]
        ]
        .assign(showdate=lambda x: pd.to_datetime(x["showdate"]))
        .sort_values("showdate")
        .reset_index(drop=True)
        .reset_index(names="show_number")
        .assign(show_number=lambda x: x["show_number"] + 1)
    )
    show_data["tourid"] = show_data["tourid"].astype("Int64").astype(str)
    return show_data, venue_data


def load_setlist_data(api_key: str) -> tuple["pd.DataFrame", "pd.DataFrame"]:
    """
    Load setlist and transition data from the Phish API.

    Args:
        api_key (str): API key for authentication.
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Tuple of DataFrames for setlist data and transition data.
    """
    try:
        setlist_data_response = make_api_request("setlists/artistid/1", api_key)
        if not setlist_data_response or "data" not in setlist_data_response:
            logger.error("Failed to retrieve setlist data or data is malformed.")
            return pd.DataFrame(), pd.DataFrame()  # Return empty DataFrames on error
        setlist_data = pd.DataFrame(setlist_data_response["data"])
        transition_data = (
            setlist_data[["transition", "trans_mark"]]
            .drop_duplicates()
            .sort_values(by=["transition"])
        )
        setlist_columns = [
            "showid",
            "uniqueid",
            "songid",
            "set",
            "position",
            "transition",
            "isreprise",
            "isjam",
            "isjamchart",
            "jamchart_description",
            "tracktime",
            "gap",
            "is_original",
            "soundcheck",
            "footnote",
            "exclude",
        ]
        setlist_df = setlist_data[setlist_columns].copy()
        return setlist_df, transition_data
    except Exception as e:
        logger.exception("CRITICAL ERROR in load_setlist_data: %s", str(e))
        raise
