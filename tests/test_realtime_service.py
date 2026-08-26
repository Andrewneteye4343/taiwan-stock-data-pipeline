import pytest

from src.services.realtime_service import (
    calculate_realtime_price_change,
    fetch_realtime_quote,
    parse_realtime_quote,
    _LAST_TRANSACTION_PRICE,

)
from unittest.mock import Mock, patch

def test_realtime_service_import():
    assert callable(fetch_realtime_quote)


def test_calculate_realtime_price_change():
    previous_close = 2400
    last_price = 2380

    change = calculate_realtime_price_change(
        last_price,
        previous_close,
    )

    assert change["change"] == -20
    assert change["change_pct"] == pytest.approx(
        -0.833333,
        rel=1e-5,
    )

def test_parse_realtime_quote():
    payload = {
        "msgArray": [
            {
                "@": "2330.tw",
                "c": "2330",
                "n": "台積電",
                "d": "20260818",
                "t": "13:30:00",
                "o": "2415.0000",
                "h": "2415.0000",
                "l": "2375.0000",
                "z": "2380.0000",
                "y": "2400.0000",
                "v": "17217",
            }
        ]
    }

    result = parse_realtime_quote(payload)

    assert result["symbol"] == "2330"
    assert result["name"] == "台積電"

    assert result["trade_date"] == "2026-08-18"
    assert result["trade_time"] == "13:30:00"

    assert result["previous_trade_price"] == 2380.0
    assert result["open"] == 2415.0
    assert result["high"] == 2415.0
    assert result["low"] == 2375.0
    assert result["previous_close"] == 2400.0

    assert result["change"] == -20.0
    assert round(result["change_pct"], 6) == round(
        -20 / 2400 * 100,
        6,
    )

    assert result["volume"] == 17217


def test_parse_realtime_quote_empty_msg_array():
    payload = {
        "msgArray": []
    }

    result = parse_realtime_quote(payload)

    assert result is None


def test_parse_realtime_quote_missing_msg_array():
    payload = {}

    result = parse_realtime_quote(payload)

    assert result is None

def test_fetch_realtime_quote():
    assert callable(fetch_realtime_quote)

def test_fetch_realtime_quote_success():
    fake_response = Mock()

    fake_response.raise_for_status.return_value = None

    fake_response.json.return_value = {
        "msgArray": [
            {
                "@": "2330.tw",
                "c": "2330",
                "n": "台積電",
                "z": "2380.0000",
                "y": "2400.0000",
                "o": "2415.0000",
                "h": "2415.0000",
                "l": "2375.0000",
                "v": "17217",
            }
        ]
    }

    with patch(
        "src.services.realtime_service.requests.get",
        return_value=fake_response,
    ) as mock_get:

        result = fetch_realtime_quote("2330")

    assert result["symbol"] == "2330"
    assert result["name"] == "台積電"
    assert result["previous_trade_price"] == 2380.0
    assert result["previous_close"] == 2400.0

    mock_get.assert_called_once()

def test_fetch_realtime_quote_http_error():
    fake_response = Mock()

    fake_response.raise_for_status.side_effect = Exception(
        "HTTP error"
    )

    with patch(
        "src.services.realtime_service.requests.get",
        return_value=fake_response,
    ):

        try:
            fetch_realtime_quote("2330")
        except Exception as exc:
            assert str(exc) == "HTTP error"
        else:
            raise AssertionError(
                "Expected HTTP error"
            )

def test_realtime_quote_has_normalized_fields():
    fake_response = Mock()

    fake_response.raise_for_status.return_value = None

    fake_response.json.return_value = {
        "msgArray": [
            {
                "@": "2330.tw",
                "c": "2330",
                "n": "台積電",
                "d": "20260818",
                "t": "13:30:00",
                "z": "2380.0000",
                "y": "2400.0000",
                "o": "2415.0000",
                "h": "2415.0000",
                "l": "2375.0000",
                "v": "17217",
            }
        ]
    }

    with patch(
        "src.services.realtime_service.requests.get",
        return_value=fake_response,
    ):

        quote = fetch_realtime_quote("2330")

    assert "symbol" in quote
    assert "name" in quote
    assert "previous_trade_price" in quote
    assert "previous_close" in quote
    assert "open" in quote
    assert "high" in quote
    assert "low" in quote
    assert "volume" in quote
    assert "trade_time" in quote
    assert "change" in quote
    assert "change_pct" in quote

def test_fetch_realtime_quote_empty_symbol():
    with pytest.raises(ValueError, match="symbol cannot be empty"):
        fetch_realtime_quote("")

def test_fetch_realtime_quote_whitespace_symbol():
    with pytest.raises(ValueError, match="symbol cannot be empty"):
        fetch_realtime_quote("   ")

def test_fetch_realtime_quote_none_symbol():
    with pytest.raises(ValueError, match="symbol cannot be empty"):
        fetch_realtime_quote(None)

def test_parse_realtime_quote_without_previous_trade_price():
    _LAST_TRANSACTION_PRICE.clear()
    payload = {
        "msgArray": [
            {
                "@": "2330.tw",
                "c": "2330",
                "n": "台積電",
                "d": "20260826",
                "t": "11:29:20",
                "o": "2375.0000",
                "h": "2420.0000",
                "l": "2375.0000",
                "z": "-",
                "y": "2400.0000",
                "v": "10252",
            }
        ]
    }

    result = parse_realtime_quote(payload)

    assert result["symbol"] == "2330"
    assert result["previous_trade_price"] is None
    assert result["change"] is None
    assert result["change_pct"] is None
    assert result["volume"] == 10252

def test_parse_realtime_quote_uses_previous_transaction_price():
    _LAST_TRANSACTION_PRICE.clear()

    first_payload = {
        "msgArray": [
            {
                "c": "2330",
                "n": "台積電",
                "d": "20260826",
                "t": "11:30:00",
                "z": "2380.0000",
                "y": "2400.0000",
                "v": "10000",
            }
        ]
    }

    first_result = parse_realtime_quote(
        first_payload
    )

    assert first_result["previous_trade_price"] == 2380.0

    second_payload = {
        "msgArray": [
            {
                "c": "2330",
                "n": "台積電",
                "d": "20260826",
                "t": "11:30:05",
                "z": "-",
                "y": "2400.0000",
                "v": "10010",
            }
        ]
    }

    second_result = parse_realtime_quote(
        second_payload
    )

    assert second_result["previous_trade_price"] == 2380.0

def test_parse_realtime_quote_does_not_use_previous_transaction_price_from_previous_day():
    _LAST_TRANSACTION_PRICE.clear()

    first_payload = {
        "msgArray": [
            {
                "@": "2330.tw",
                "c": "2330",
                "n": "台積電",
                "d": "20260826",
                "t": "13:30:00",
                "z": "2380.0000",
                "y": "2400.0000",
                "v": "10000",
            }
        ]
    }

    first_result = parse_realtime_quote(
        first_payload
    )

    assert first_result["trade_date"] == "2026-08-26"
    assert first_result["previous_trade_price"] == 2380.0

    second_payload = {
        "msgArray": [
            {
                "@": "2330.tw",
                "c": "2330",
                "n": "台積電",
                "d": "20260827",
                "t": "09:00:05",
                "z": "-",
                "y": "2380.0000",
                "v": "10",
            }
        ]
    }

    second_result = parse_realtime_quote(
        second_payload
    )

    assert second_result["trade_date"] == "2026-08-27"

    assert (
        second_result["previous_trade_price"]
        is None
    )

    assert second_result["change"] is None
    assert second_result["change_pct"] is None