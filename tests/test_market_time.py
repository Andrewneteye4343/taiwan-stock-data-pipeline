from datetime import datetime
from zoneinfo import ZoneInfo

from src.core.market_time import (
    is_market_open_at,
)


TAIPEI = ZoneInfo("Asia/Taipei")


def make_datetime(
    hour: int,
    minute: int = 0,
    second: int = 0,
) -> datetime:
    """
    Create a Taiwan-local datetime.
    """

    return datetime(
        2026,
        8,
        25,
        hour,
        minute,
        second,
        tzinfo=TAIPEI,
    )


def test_market_closed_before_0900():
    current_time = make_datetime(8, 59)

    assert is_market_open_at(current_time) is False


def test_market_open_exactly_at_0900():
    current_time = make_datetime(9, 0)

    assert is_market_open_at(current_time) is True


def test_market_open_during_trading_hours():
    current_time = make_datetime(10, 30)

    assert is_market_open_at(current_time) is True


def test_market_open_at_1329():
    current_time = make_datetime(13, 29)

    assert is_market_open_at(current_time) is True


def test_market_closed_exactly_at_1330():
    current_time = make_datetime(13, 30)

    assert is_market_open_at(current_time) is False


def test_market_closed_after_1330():
    current_time = make_datetime(14, 0)

    assert is_market_open_at(current_time) is False
