"""
Goose Data Loaders
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
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
logs_dir = os.path.join(project_root, "logs", "Goose")
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "goose_pipeline.log")
logger = get_logger(__name__, log_file=log_file, add_console_handler=True)


def load_song_data() -> "pd.DataFrame":
    """
    Load and process Goose song data from API and website scrape.

    Returns:
        pd.DataFrame: DataFrame containing merged song data.
    """
    song_table_idx = 1
    songdata_api = pd.DataFrame(make_api_request("songs", "v2")["data"]).drop(
        columns=["slug", "created_at", "updated_at"], errors="ignore"
    )
    response = requests.get("https://elgoose.net/song/", timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    tables = pd.read_html(StringIO(str(soup.find_all("table"))))
    if not tables or len(tables) <= song_table_idx:
        logger.error(
            "Expected table at index %d not found in Goose song page.", song_table_idx
        )
        return pd.DataFrame()
    songdata_scrape = (
        tables[song_table_idx].sort_values(by="Song Name").reset_index(drop=True)
    )
    merged_data = songdata_api.merge(
        songdata_scrape, left_on="name", right_on="Song Name", how="inner"
    )
    columns = [
        "id",
        "Song Name",
        "isoriginal",
        "Original Artist",
        "Debut Date",
        "Last Played",
        "Times Played Live",
        "Avg Show Gap",
    ]
    merged_data = merged_data[columns].copy()
    final_columns = {
        "id": "song_id",
        "Song Name": "song",
        "isoriginal": "is_original",
        "Original Artist": "original_artist",
        "Debut Date": "debut_date",
        "Last Played": "last_played",
        "Times Played Live": "times_played",
        "Avg Show Gap": "avg_show_gap",
    }
    return merged_data.rename(columns=final_columns)


def load_show_data() -> tuple["pd.DataFrame", "pd.DataFrame", "pd.DataFrame"]:
    """
    Load and process Goose show, venue, and tour data.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        Tuple of DataFrames for show data, venue data, and tour data.
    """
    today = datetime.today().strftime("%Y-%m-%d")
    shows = pd.DataFrame(make_api_request("shows", "v2")["data"])
    past_shows = shows[shows["showdate"] < today]
    future_shows = shows[shows["showdate"] >= today].sort_values("showdate").head(1)
    all_shows = pd.concat([past_shows, future_shows])
    all_shows = (
        all_shows[(all_shows["artist"] == "Goose")].copy().reset_index(drop=True)
    )
    venue_data = (
        all_shows[["venue_id", "venuename", "city", "state", "country", "location"]]
        .drop_duplicates()
        .sort_values("venue_id")
        .reset_index(drop=True)
        .rename(columns={"venue": "venue_name"})
    )
    tour_data = (
        all_shows[["tour_id", "tourname"]]
        .drop_duplicates()
        .sort_values("tour_id")
        .reset_index(drop=True)
    )
    show_data = (
        all_shows[["show_id", "showdate", "venue_id", "tour_id", "showorder"]]
        .sort_values("showdate")
        .reset_index(names="show_number")
        .rename(columns={"showdate": "show_date", "showorder": "show_order"})
        .assign(show_number=lambda x: x["show_number"] + 1)
    )
    show_data["tour_id"] = show_data["tour_id"].astype("Int64").astype(str)
    return show_data, venue_data, tour_data


def load_setlist_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and process Goose setlist and transition data.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Tuple of DataFrames for setlist data and transition data.
    """
    setlist_df = pd.DataFrame(make_api_request("setlists", "v1")["data"])
    transition_data = (
        setlist_df[["transition_id", "transition"]]
        .drop_duplicates()
        .sort_values(by=["transition_id"])
    )
    setlist_data = (
        setlist_df[setlist_df["artist"] == "Goose"].copy().reset_index(drop=True)
    )
    setlist_columns = [
        "uniqueid",
        "show_id",
        "song_id",
        "setnumber",
        "position",
        "tracktime",
        "transition_id",
        "isreprise",
        "isjam",
        "footnote",
        "isjamchart",
        "jamchart_notes",
        "soundcheck",
        "isverified",
        "isrecommended",
    ]
    return setlist_data[setlist_columns], transition_data
