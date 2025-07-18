"""Formatting utilities for next show and dataframe display in Jam Band Nerd app."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd


def format_next_show_wsp(data: Dict[str, Any]) -> Optional[str]:
    """Format next show string for WSP using all available fields.

    Args:
        data (Dict[str, Any]): Next show info.
    Returns:
        Optional[str]: Formatted string or None.
    """
    date = data.get("date")
    venue = data.get("venue")
    city = data.get("city")
    state = data.get("state")
    if date:
        try:
            date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        except Exception:
            date_fmt = date
    else:
        date_fmt = None
    # Unified formatting: always 'Next show: <Date> at <Venue> in <City>, <State>'
    parts = [f"Next show: {date_fmt}"] if date_fmt else []
    if venue:
        parts.append(f"at {venue}")
    if city:
        if not venue:
            parts.append(f"in {city}")
        else:
            parts[-1] += f" in {city}"
    if state and state != "UU":
        if city or venue:
            parts[-1] += f", {state}"
        else:
            parts.append(f"in {state}")
    return " ".join(parts) if parts else None


def format_next_show_um(data: Dict[str, Any]) -> Optional[str]:
    """Format next show string for UM using available fields.

    Args:
        data (Dict[str, Any]): Next show info.
    Returns:
        Optional[str]: Formatted string or None.
    """
    venue = data.get("Venue Name")
    city = data.get("City")
    state = data.get("State")
    date = data.get("Last Played")
    if date:
        try:
            date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        except Exception:
            date_fmt = date
    else:
        date_fmt = None
    # Unified formatting: always 'Next show: <Date> at <Venue> in <City>, <State>'
    parts = [f"Next show: {date_fmt}"] if date_fmt else []
    if venue:
        parts.append(f"at {venue}")
    if city:
        if not venue:
            parts.append(f"in {city}")
        else:
            parts[-1] += f" in {city}"
    if state:
        if city or venue:
            parts[-1] += f", {state}"
        else:
            parts.append(f"in {state}")
    return " ".join(parts) if parts else None


def format_next_show_phish_goose(
    data: Dict[str, Any],
    showdata_path: Path,
    venuedata_path: Path,
    date_field: str = "show_date",
) -> Optional[str]:
    """Format next show string for Phish and Goose using showdata.csv and venuedata.csv as lookup.

    Args:
        data (Dict[str, Any]): Parsed next_show.json['next_show']
        showdata_path (Path): Path to showdata.csv
        venuedata_path (Path): Path to venuedata.csv
        date_field (str): Date field to use from JSON
    Returns:
        Optional[str]: Formatted next show string, or None if not enough info
    """
    date = data.get(date_field) or data.get("showdate")
    # Use venue_name, city, state directly if present
    venue = data.get("venue_name")
    city = data.get("city")
    state = data.get("state")
    if date and venue and city and state:
        try:
            date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        except Exception:
            date_fmt = date
        return f"Next show: {date_fmt} at {venue} in {city}, {state}"
    # Fallback to CSV lookup logic if any field missing
    venue_id_json = data.get("venue_id") or data.get("venueid")
    if not date or not showdata_path.exists() or not venuedata_path.exists():
        if date:
            try:
                date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
            except Exception:
                date_fmt = date
            return f"Next show: {date_fmt}"
        return None
    try:
        show_df = pd.read_csv(showdata_path)
        venue_df = pd.read_csv(venuedata_path)
        date_cols = [col for col in show_df.columns if "date" in col.lower()]
        found = None
        for dcol in date_cols:
            match = show_df[show_df[dcol] == date]
            if not match.empty:
                found = match.iloc[0]
                break
            try:
                show_df[dcol] = pd.to_datetime(
                    show_df[dcol], errors="coerce"
                ).dt.strftime("%Y-%m-%d")
                match = show_df[show_df[dcol] == date]
                if not match.empty:
                    found = match.iloc[0]
                    break
            except Exception as ex:
                continue
        if found is None and venue_id_json is not None:
            venue_id_json_str = str(venue_id_json)
            venue_id_cols = [
                col
                for col in show_df.columns
                if "venue_id" in col.lower() or "venueid" in col.lower()
            ]
            for vcol in venue_id_cols:
                match = show_df[show_df[vcol].astype(str) == venue_id_json_str]
                if not match.empty:
                    found = match.sort_values(
                        by=date_cols[0] if date_cols else vcol, ascending=False
                    ).iloc[0]
                    break
        try:
            date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        except Exception:
            date_fmt = date
        venue, city, state = None, None, None
        venue_id = None
        if found is not None:
            venue_id = found.get("venueid") or found.get("venue_id") or venue_id_json
        else:
            venue_id = venue_id_json
        if venue_id is not None:
            venue_id_str = str(venue_id)
            # Determine the correct venue ID column
            if "venue_id" in venue_df.columns:
                venue_id_col = "venue_id"
            elif "venueid" in venue_df.columns:
                venue_id_col = "venueid"
            else:
                venue_id_col = None
            venue_matches = pd.DataFrame()
            if venue_id_col:
                venue_matches = venue_df[
                    venue_df[venue_id_col].astype(str) == venue_id_str
                ]
            if not venue_matches.empty:
                vrow = venue_matches.iloc[0]
                # Determine the correct venue name column
                if "venue" in vrow:
                    venue = vrow["venue"]
                elif "venuename" in vrow:
                    venue = vrow["venuename"]
                else:
                    venue = None
                city = vrow["city"] if "city" in vrow else None
                state = vrow["state"] if "state" in vrow else None
        if found is not None:
            venue = (
                venue
                or found.get("venue")
                or found.get("Venue Name")
                or found.get("venue_name")
            )
            city = city or found.get("city") or found.get("City")
            state = state or found.get("state") or found.get("State")
        # Unified formatting: always 'Next show: <Date> at <Venue> in <City>, <State>'
        parts = [f"Next show: {date_fmt}"] if date_fmt else []
        if venue:
            parts.append(f"at {venue}")
        if city:
            if not venue:
                parts.append(f"in {city}")
            else:
                parts[-1] += f" in {city}"
        if state:
            if city or venue:
                parts[-1] += f", {state}"
            else:
                parts.append(f"in {state}")
        return " ".join(parts) if parts else None
    except Exception:
        try:
            date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        except Exception:
            date_fmt = date
        return f"Next show: {date_fmt}"
    return None
