from datetime import datetime

def validate_date_format(date: str) -> None:
    """
    Validate that a date string is in the "YYYY-MM-DD" format.

    :param date: str: The date string to validate.
    :raises ValueError: If the date is not in the correct format.
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: '{date}'. Expected format is 'YYYY-MM-DD'.")
