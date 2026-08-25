from datetime import date
from pathlib import Path

import yaml

from src.calendar.twse_calendar import (
    TWSECalendarProvider,
)


CONFIG_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "config"
    / "trading_calendar.yaml"
)


DAY_NAME_TO_WEEKDAY = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


def load_calendar_config() -> dict:
    """
    Load trading calendar configuration from YAML.
    """

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Trading calendar config not found: {CONFIG_PATH}"
        )

    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError(
            "Trading calendar configuration "
            "must be a mapping"
        )

    if "market" not in config:
        raise ValueError(
            "Missing 'market' configuration"
        )

    market_config = config["market"]

    if not isinstance(market_config, dict):
        raise ValueError(
            "'market' configuration must be a mapping"
        )

    return market_config


def is_trading_day(
    target_date: date,
    config: dict | None = None,
    provider=None,
) -> bool:
    """
    Determine whether a date is a TWSE trading day.

    Rules:
    1. Saturday and Sunday are always non-trading days.
    2. TWSE official closed-market dates are non-trading days.
    3. Locally configured holidays are also non-trading days.

    Parameters
    ----------
    target_date:
        Date to evaluate.

    config:
        Optional local calendar configuration.

    provider:
        Optional TWSE calendar provider.
        Primarily useful for testing.
    """

    if config is None:
        config = load_calendar_config()

    weekend_names = config.get(
        "weekend",
        [],
    )

    holidays = config.get(
        "holidays",
        [],
    )

    weekend_days = {
        DAY_NAME_TO_WEEKDAY[name]
        for name in weekend_names
        if name in DAY_NAME_TO_WEEKDAY
    }

    if target_date.weekday() in weekend_days:
        return False

    if target_date.isoformat() in holidays:
        return False

    if provider is None:
        provider = TWSECalendarProvider()

    closed_dates = provider.get_closed_dates()

    if target_date in closed_dates:
        return False

    return True