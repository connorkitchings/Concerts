import json
import os
from typing import Optional


def update_date_updated(band: str, prediction_type: str, datetime_str: str) -> None:
    """
    Update or create a date_updated.json file for a band's predictions folder in 3 - Data, storing the last updated datetime per prediction type.

    Args:
        band (str): The band name (e.g., 'WSP', 'Phish').
        prediction_type (str): The prediction type ('CK+' or 'Notebook').
        datetime_str (str): The datetime string to record (ISO format).
    """
    # Find project root (assume this script is in 2 - Make Predictions)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    data_dir = os.path.join(project_root, '3_DataStorage', band, 'Meta')
    os.makedirs(data_dir, exist_ok=True)
    json_path = os.path.join(data_dir, 'date_updated.json')

    # Load or initialize
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    data[prediction_type] = datetime_str

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
