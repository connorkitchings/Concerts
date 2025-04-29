import os
from pathlib import Path
from datetime import datetime

def get_data_dir():
    current_dir = Path(__file__).resolve()
    return current_dir.parent.parent.parent / '3 - Data' / 'Goose' / 'ElGoose'

def get_date_and_time():
    return datetime.now().strftime('%m/%d/%Y %H:%M')
