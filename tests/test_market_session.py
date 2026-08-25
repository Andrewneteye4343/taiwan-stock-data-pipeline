from datetime import datetime

from src.core.market_session import (
    MarketSession,
    get_market_session,
)


class FakeTWSECalendarProvider:
    """
    Fake calendar provider for deterministic tests.

    No special closed dates are configured here.
    """

    def get_closed_dates(self):
        return set()


def make_datetime(
    hour: int,
    minute: int = 0,
    second: int = 0,
) -> datetime:
    """
    Create a Taiwan-local datetime for a known trading day.
    """

    return datetime(
        2026,
        8,
        25,
        hour,
        minute,
        second,
    )


def test_before_market_open():
    current_time = make_datetime(8, 59)

    result = get_market_session(
        current_time=current_time,
    )

    assert result == MarketSession.PRE_OPEN


def test_market_open_exactly_at_0900():
    current_time = make_datetime(9, 0)

    result = get_market_session(
        current_time=current_time,
    )

    assert result == MarketSession.TRADING


def test_during_market_hours():
    current_time = make_datetime(10, 30)

    result = get_market_session(
        current_time=current_time,
    )

    assert result == MarketSession.TRADING


def test_before_market_close():
    current_time = make_datetime(13, 29)

    result = get_market_session(
        current_time=current_time,
    )

    assert result == MarketSession.TRADING


def test_market_close_exactly_at_1330():
    current_time = make_datetime(13, 30)

    result = get_market_session(
        current_time=current_time,
    )

    assert result == MarketSession.POST_CLOSE


def test_after_market_close():
    current_time = make_datetime(14, 0)

    result = get_market_session(
        current_time=current_time,
    )

    assert result == MarketSession.POST_CLOSE


def test_weekend_is_closed():
    # 2026-08-29 is Saturday.
    current_time = datetime(
        2026,
        8,
        29,
        10,
        0,
    )

    result = get_market_session(
        current_time=current_time,
    )

    assert result == MarketSession.CLOSED