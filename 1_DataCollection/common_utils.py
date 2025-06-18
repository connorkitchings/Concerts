import os
from datetime import datetime
from pathlib import Path

import common_config


def print_relative_path(path: "str | Path") -> None:
    """
    Print the given file or directory path relative to the first occurrence of 'Concerts/'.

    Args:
        path (str or Path): File or directory path to print.
    Returns:
        None
    """
    path_str = str(path)
    marker = "Concerts" + "/"
    idx = path_str.find(marker)
    if idx == -1:
        marker = "Concerts" + "\\"
        idx = path_str.find(marker)
    if idx == -1:
        marker = "Concerts"
        idx = path_str.find(marker)
    if idx != -1:
        print(path_str[idx:])
    else:
        print(path_str)


def get_date_and_time() -> str:
    """
    Get the current date and time as a formatted string using common_config.DATETIME_FORMAT.

    Returns:
        str: Current date and time in 'YYYY-MM-DD HH:MM:SS' format.
    """
    return datetime.now().strftime(common_config.DATETIME_FORMAT)
