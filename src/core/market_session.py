from enum import Enum
from datetime import datetime, time

from src.calendar.trading_calendar import is_trading_day
from src.core.market_time import now


class MarketSession(str, Enum):
    """
    Taiwan stock market session states.
    """

    CLOSED = "CLOSED"
    PRE_OPEN = "PRE_OPEN"
    TRADING = "TRADING"
    POST_CLOSE = "POST_CLOSE"


MARKET_OPEN_TIME = time(9, 0)
MARKET_CLOSE_TIME = time(13, 30)


def get_market_session(
    current_time: datetime | None = None,
) -> MarketSession:
    """
    Determine the current Taiwan stock market session.

    Parameters
    ----------
    current_time : datetime | None
        Taiwan-local datetime.
        If omitted, current Taiwan time is used.

    Returns
    -------
    MarketSession
        Current market session.
    """

    if current_time is None:
        current_time = now()

    current_date = current_time.date()
    current_clock = current_time.time()

    # ----------------------------------------
    # Non-trading day
    # ----------------------------------------

    if not is_trading_day(current_date):
        return MarketSession.CLOSED

    # ----------------------------------------
    # Trading day before market opens
    # ----------------------------------------

    if current_clock < MARKET_OPEN_TIME:
        return MarketSession.PRE_OPEN

    # ----------------------------------------
    # Trading session
    # ----------------------------------------

    if current_clock < MARKET_CLOSE_TIME:
        return MarketSession.TRADING

    # ----------------------------------------
    # After market closes
    # ----------------------------------------

    return MarketSession.POST_CLOSE