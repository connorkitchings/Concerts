from datetime import datetime
from pathlib import Path

def get_date_and_time() -> str:
    """
    Get the current date and time as a formatted string.

    Returns:
        str: Current date and time in 'MM/DD/YYYY HH:MM' format.
    """
    return datetime.now().strftime('%m/%d/%Y %H:%M')

def date_format_for_all(date_str: str) -> str:
    """
    Convert a date string to 'MM/DD/YYYY' format.

    Args:
        date_str (str): Input date string in 'MM/DD/YYYY' format.
    Returns:
        str: Standardized date string in 'MM/DD/YYYY' format.
    """
    return datetime.strptime(date_str, '%m/%d/%Y').strftime('%m/%d/%Y')

def print_relative_path(path: 'str | Path') -> None:
    """
    Print the given file or directory path relative to the first occurrence of 'Concerts/'.

    Args:
        path (str or Path): File or directory path to print.
    Returns:
        None
    """
    path_str = str(path)
    marker = 'Concerts' + '/'
    idx = path_str.find(marker)
    if idx == -1:
        marker = 'Concerts' + '\\'
        idx = path_str.find(marker)
    if idx == -1:
        marker = 'Concerts'
        idx = path_str.find(marker)
    if idx != -1:
        print(path_str[idx:])
    else:
        print(path_str)