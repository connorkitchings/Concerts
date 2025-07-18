"""
Prediction utilities for ckplus
"""

import json
import os
import pathlib

# NOTE: For 'from utils.logger import ...' to work, run scripts from the CKPlus root directory
# and mark CKPlus as the source root in your IDE. For local dev,
# you may temporarily adjust sys.path.
from utils.logger import get_logger, restrict_to_repo_root


def update_date_updated(band: str, model: str, date_str: str) -> None:
    """
    Updates the date_updated.json file for the given band/model in data/<band>/generated/.

    Args:
        band (str): Band name (e.g., 'Goose')
        model (str): Model name (e.g., 'CK+')
        date_str (str): ISO-formatted datetime string
    """
    logger = get_logger(__name__)
    try:
        # Find project root (parent of 'src')
        script_dir = pathlib.Path(__file__).resolve().parent
        for parent in script_dir.parents:
            if parent.name == "src":
                project_root = parent.parent
                break
        else:
            project_root = script_dir.parents[3]
        meta_folder = project_root / "data" / band / "generated"
        os.makedirs(meta_folder, exist_ok=True)
        json_path = meta_folder / "date_updated.json"
        # Load existing data if file exists
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    all_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                all_data = {}
        else:
            all_data = {}
        all_data[model] = {"band": band, "model": model, "date_updated": date_str}
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2)
        logger.info(
            "Updated date_updated.json for %s/%s at %s",
            band,
            model,
            restrict_to_repo_root(json_path),
        )
    except OSError as e:
        logger.error("Failed to update date_updated.json: %s", str(e))
