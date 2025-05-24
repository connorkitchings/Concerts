"""
Data loading utilities for the Jam Band Predictions API.
"""
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union

import pandas as pd

# Base directory for data
DATA_DIR = Path("/Users/connorkitchings/Desktop/Repositories/Concerts/3 - Data")

def get_next_show_info(band: str) -> Dict[str, Any]:
    """
    Get information about the next show for a band.
    
    Args:
        band: Short name of the band (e.g., "WSP", "Goose")
        
    Returns:
        Dict[str, Any]: Next show information with date, venue, city, and state
    """
    path = DATA_DIR / band / "From Web" / "next_show.json"
    if not path.exists():
        return {}
    
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            show_info = data.get("next_show", {})
    except Exception:
        return {}
    
    # For Phish, merge with venuedata.csv to get venue, city, state
    if band == "Phish" and show_info and "venueid" in show_info:
        venue_path = DATA_DIR / band / "From Web" / "venuedata.csv"
        if venue_path.exists():
            try:
                venues = pd.read_csv(venue_path, dtype={"venueid": str})
                # venueid in show_info may be int or str, ensure both are str for merge
                show_venueid = str(show_info["venueid"])
                venue_row = venues[venues["venueid"].astype(str) == show_venueid]
                if not venue_row.empty:
                    venue_row = venue_row.iloc[0]
                    return {
                        "date": show_info.get("showdate", ""),
                        "venue": venue_row["venue"],
                        "city": venue_row["city"],
                        "state": venue_row["state"]
                    }
            except Exception:
                pass
        # fallback: just return showdate
        return {"date": show_info.get("showdate", "")}
    
    return show_info

def get_last_updated_time(band: str) -> str:
    """
    Get the last time data was updated for a band.
    
    Args:
        band: Short name of the band (e.g., "WSP", "Goose")
        
    Returns:
        str: Formatted last updated time or "Unknown" if not available
    """
    path = DATA_DIR / band / "From Web" / "last_updated.json"
    
    if not path.exists():
        return "Unknown"
    
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            last_updated = data.get("last_updated", "Unknown")
            
            # Format date if it's a valid ISO date
            try:
                if last_updated != "Unknown":
                    dt = datetime.datetime.fromisoformat(last_updated)
                    return dt.strftime('%B %d, %Y %I:%M %p')
            except Exception:
                pass
            
            return last_updated
    except Exception:
        return "Unknown"

def load_prediction_data(band: str, prediction_type: str) -> pd.DataFrame:
    """
    Load prediction data for a specific band and prediction type.
    
    Args:
        band: Short name of the band (e.g., "WSP", "Goose")
        prediction_type: Type of prediction ("notebook" or "ckplus")
        
    Returns:
        pd.DataFrame: Prediction data
    """
    file_prefix = "todays"
    filename = f"{file_prefix}{prediction_type}.csv"
    path = DATA_DIR / band / "Predictions" / filename
    
    if not path.exists():
        return pd.DataFrame()
    
    try:
        data = pd.read_csv(path)
        
        # For notebook predictions, rename columns for consistency
        if prediction_type == "notebook":
            data.columns = [
                "Song", 
                "Times Played in Last Year", 
                "Last Time Played", 
                "Current Gap", 
                "Average Gap", 
                "Median Gap"
            ]
        
        return data
    except Exception:
        return pd.DataFrame()

def get_song_history(band: str, song_name: str) -> Dict[str, Any]:
    """
    Get historical performance data for a specific song.
    
    Args:
        band: Short name of the band (e.g., "WSP", "Goose")
        song_name: Name of the song
        
    Returns:
        Dict[str, Any]: Song history data
    """
    # This function is a placeholder for future implementation
    # In a real implementation, you would query your historical data
    return {
        "name": song_name,
        "band": band,
        "total_plays": 0,
        "first_played": "",
        "last_played": "",
        "shows": []
    }
