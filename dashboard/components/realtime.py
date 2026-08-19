import streamlit as st

from src.services.realtime_service import (
    fetch_realtime_quote,
)


@st.cache_data(ttl=60)
def load_realtime_quote(symbol):
    """
    Load realtime quote for a stock symbol.

    Parameters
    ----------
    symbol : str
        Taiwan stock symbol, e.g. "2330".

    Returns
    -------
    dict | None
        Normalized realtime quote.
        Returns None when the realtime API request fails.
    """

    try:
        return fetch_realtime_quote(symbol)

    except Exception as exc:
        st.error(
            f"Realtime quote error: {type(exc).__name__}: {exc}"
        )
        return None


def normalize_refresh_interval(
    interval,
):
    """
    Validate realtime refresh interval.

    Allowed intervals:
    - 30 seconds
    - 60 seconds
    - 300 seconds
    """

    allowed_intervals = {
        30,
        60,
        300,
    }

    if interval in allowed_intervals:
        return interval

    return 60


def get_refresh_options():
    """
    Return available realtime refresh options.
    """

    return {
        "30 秒": 30,
        "60 秒": 60,
        "5 分鐘": 300,
    }