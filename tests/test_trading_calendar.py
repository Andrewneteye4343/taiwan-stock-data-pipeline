from datetime import date

from src.calendar.trading_calendar import (
    is_trading_day,
)


def test_monday_is_trading_day():
    target = date(2026, 8, 24)

    assert is_trading_day(target) is True


def test_tuesday_is_trading_day():
    target = date(2026, 8, 25)

    assert is_trading_day(target) is True


def test_friday_is_trading_day():
    target = date(2026, 8, 28)

    assert is_trading_day(target) is True


def test_saturday_is_not_trading_day():
    target = date(2026, 8, 29)

    assert is_trading_day(target) is False


def test_sunday_is_not_trading_day():
    target = date(2026, 8, 30)

    assert is_trading_day(target) is False

def test_configured_holiday_is_not_trading_day():
    target = date(2026, 1, 1)

    config = {
        "weekend": [
            "Saturday",
            "Sunday",
        ],
        "holidays": [
            "2026-01-01",
        ],
    }

    assert is_trading_day(
        target,
        config=config,
    ) is False

def test_non_holiday_weekday_is_trading_day():
    target = date(2026, 1, 2)

    config = {
        "weekend": [
            "Saturday",
            "Sunday",
        ],
        "holidays": [
            "2026-01-01",
        ],
    }

    assert is_trading_day(
        target,
        config=config,
    ) is True