from datetime import date, datetime, time
from zoneinfo import ZoneInfo


MARKET_TIMEZONE = ZoneInfo("Asia/Taipei")

MARKET_OPEN_TIME = time(9, 0)
MARKET_CLOSE_TIME = time(13, 30)


def now() -> datetime:
    """
    Return current datetime in Taiwan market timezone.
    """

    return datetime.now(MARKET_TIMEZONE)


def today() -> date:
    """
    Return current date in Taiwan market timezone.
    """

    return now().date()


def current_time() -> time:
    """
    Return current local time in Taiwan market timezone.
    """

    return now().time()


def is_market_open_at(current: datetime) -> bool:
    """
    Return whether the given datetime falls within
    regular Taiwan stock market trading hours.

    Trading session:
        09:00 <= time < 13:30
    """

    local_time = current.astimezone(
        MARKET_TIMEZONE
    ).time()

    return (
        MARKET_OPEN_TIME
        <= local_time
        < MARKET_CLOSE_TIME
    )


def is_market_open() -> bool:
    """
    Return whether the Taiwan stock market is
    currently open.
    """

    return is_market_open_at(now())