from unittest.mock import patch

from dashboard.components.realtime import (
    load_realtime_quote,
)


def test_load_realtime_quote():
    load_realtime_quote.clear()

    mock_quote = {
        "symbol": "2330",
        "name": "台積電",
        "last_price": 2380.0,
        "previous_close": 2400.0,
        "change": -20.0,
        "change_pct": -0.8333333333,
        "open": 2415.0,
        "high": 2415.0,
        "low": 2375.0,
        "volume": 17217,
        "trade_date": "2026-08-18",
        "trade_time": "13:30:00",
    }

    with patch(
        "dashboard.components.realtime.fetch_realtime_quote"
    ) as mock_fetch:

        mock_fetch.return_value = mock_quote

        result = load_realtime_quote("2330")

        assert result["symbol"] == "2330"
        assert result["name"] == "台積電"
        assert result["last_price"] == 2380.0
        assert result["change"] == -20.0

        mock_fetch.assert_called_once_with("2330")


def test_load_realtime_quote_returns_none_when_api_fails():
    load_realtime_quote.clear()

    with patch(
        "dashboard.components.realtime.fetch_realtime_quote"
    ) as mock_fetch:

        mock_fetch.side_effect = Exception(
            "API connection failed"
        )

        result = load_realtime_quote("2330")

        assert result is None