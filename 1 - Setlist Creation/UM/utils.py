def get_data_dir():
    from pathlib import Path
    current_dir = Path(__file__).resolve()
    return current_dir.parent.parent.parent / '3 - Data' / 'UM' / 'AllThingsUM'

def get_date_and_time():
    from datetime import datetime
    return datetime.now().strftime('%m/%d/%Y %H:%M')

def get_last_update_time(data_dir):
    import os
    import json
    last_updated_path = os.path.join(data_dir, "last_updated.json")
    if os.path.exists(last_updated_path):
        with open(last_updated_path, "r") as f:
            meta = json.load(f)
            return meta.get("last_updated")
    return None
