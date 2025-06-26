"""UI components for Jam Band Nerd app."""

from typing import Optional

import streamlit as st


def display_method_explanation(file_label: str) -> None:
    """
    Display an explanation of the selected prediction method.

    Args:
        file_label: String indicating prediction method ("CK+" or "Notebook")
    """
    method_explanations = {
        "CK+": (
            """
<div style='font-size:0.95em; color:#fff; margin-bottom:10px;'>
<b>CK+ Method:</b> This method uses a machine learning model trained on historical setlists and song transitions to predict the most likely songs for the next show. It incorporates recency, rarity, and show-to-show transitions to generate a ranked list and highlight songs with a high probability of being played tonight.
</div>
            """
        ),
        "Notebook": (
            """
<div style='font-size:0.95em; color:#fff; margin-bottom:10px;'>
<b>Notebook Method:</b> Inspired by Phish.net's "Trey's Notebook," this method predicts setlists by focusing on songs played most frequently in the last year, while excluding songs played in the last three shows. It identifies songs that are in rotation but not overplayed, ranking them by recent play frequency and providing stats like last played date and average gap.
</div>
            """
        ),
    }

    st.sidebar.markdown(method_explanations.get(file_label, ""), unsafe_allow_html=True)


def display_disclaimer(
    pred_date_str: str, pred_time_str: str, data_date_str: str, data_time_str: str
) -> None:
    """
    Display a disclaimer with prediction and data collection timestamps.

    Args:
        pred_date_str: Date when prediction was made
        pred_time_str: Time when prediction was made
        data_date_str: Date when data was collected
        data_time_str: Time when data was collected
    """
    disclaimer = f"<div style='font-size:0.9em; color:#888; margin-top:12px; text-align:center;'>Predictions made on {pred_date_str} at {pred_time_str} with data collected on {data_date_str} at {data_time_str}. </div>"
    st.markdown(disclaimer, unsafe_allow_html=True)


def display_next_show(next_show_str: Optional[str]) -> None:
    """
    Display next show information if available.

    Args:
        next_show_str: Formatted next show string or None
    """
    if next_show_str:
        # Capitalize 'Next Show' if present
        if next_show_str.lower().startswith("next show:"):
            next_show_str = "Next Show:" + next_show_str[9:]
        st.markdown(
            f"<h4 style='text-align: center; color: #fff;'>{next_show_str}</h4>",
            unsafe_allow_html=True,
        )
