"""
Prediction utilities for ckplus
"""

import json
import os

# NOTE: For 'from utils.logger import ...' to work, run scripts from the CKPlus root directory
# and mark CKPlus as the source root in your IDE. For local dev,
# you may temporarily adjust sys.path.
from predictions.ckplus.utils.logger import get_logger, restrict_to_repo_root


def update_date_updated(band: str, model: str, date_str: str) -> None:
    """
    Updates the date_updated.json file for the given band/model in 3_DataStorage/<band>/Meta/.

    Args:
        band (str): Band name (e.g., 'Goose')
        model (str): Model name (e.g., 'CK+')
        date_str (str): ISO-formatted datetime string
    """
    logger = get_logger(__name__)
    try:
        root_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        meta_folder = os.path.join(root_dir, f"3_DataStorage/{band}/Meta")
        os.makedirs(meta_folder, exist_ok=True)
        json_path = os.path.join(meta_folder, "date_updated.json")
        data = {"band": band, "model": model, "date_updated": date_str}
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(
            "Updated date_updated.json for %s/%s at %s",
            band,
            model,
            restrict_to_repo_root(json_path),
        )
    except OSError as e:
        logger.error("Failed to update date_updated.json: %s", str(e))
