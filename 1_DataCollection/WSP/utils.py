from datetime import datetime


def date_format_for_all(date_str: str) -> str:
    """
    Convert a date string to 'MM/DD/YYYY' format.

    Args:
        date_str (str): Input date string in 'MM/DD/YYYY' format.
    Returns:
        str: Standardized date string in 'MM/DD/YYYY' format.
    """
    return datetime.strptime(date_str, "%m/%d/%Y").strftime("%m/%d/%Y")
