from datetime import date, timedelta


def get_date_range(
    start_date: date,
    end_date: date,
) -> list[date]:
    """
    Return all dates after start_date up to end_date.

    Parameters
    ----------
    start_date : date
        Last date already stored in database.

    end_date : date
        Target date.

    Returns
    -------
    list[date]
        Dates that should be checked.
    """

    if start_date >= end_date:
        return []

    dates = []

    current_date = start_date + timedelta(days=1)

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates